import os
import random
import uuid
from datetime import datetime
from typing import List, Optional

import faker
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

import database.models as models
from backend.auth import Role, get_current_user, get_current_user_with_role
from backend.routers.common import generate_models
from backend.utills.utills import (
    get_random_measurement_directory,
    get_random_radioisotopes,
    get_random_tags,
    get_random_user,
)
from database.database import get_session_local
from loguru import logger

PICTURES_DIR = os.environ.get("PICTURES_DIR", "pictures")

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])


class MeasurementBase(BaseModel):
    name: str = Field(..., example="Measurement Name")
    description: str = Field(
        ..., example="A detailed description of the measurement"
    )
    directory: str = Field(..., example="/path/to/directory")
    number_of_files: int = Field(..., example=5)
    patient_reference: str = Field(..., example="Patient Reference")
    shifter_id: int = Field(..., example=1)


class CommentPictureResponse(BaseModel):
    id: int
    path: str
    comment_id: int

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: int
    content: str
    user: dict
    measurement_id: int
    created_at: str
    pictures: List[CommentPictureResponse] = []

    class Config:
        from_attributes = True


def generate_fake_measurement(db: Session = None):
    all_measurement_directory = db.query(
        models.MeasurementDirectory.id
    ).order_by(func.random())
    measurement_directory_list = [dir.id for dir in all_measurement_directory]
    measurement_directory_list_size = len(measurement_directory_list)
    i = 0
    while True:
        measurement_directory_id = measurement_directory_list[
            i % measurement_directory_list_size
        ]
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            # directory="/".join(
            #     [generator.catch_phrase().partition(" ")[0] for _ in range(2)]
            # ),
            directory_id=measurement_directory_id,
            number_of_files=random.randint(1, 10),
            patient_reference=generator.text(max_nb_chars=200),
            shifter_id=get_random_user(db).id,
            tags=get_random_tags(db, random.randint(0, 2)),
            radioisotopes=get_random_radioisotopes(db, random.randint(0, 2)),
        )
        i += 1


def generate_measurement(
    name: str,
    description: str,
    directory: str,
    number_of_files: int,
    patient_reference: str,
    shifter_id: int,
    measuerement_directory_id: int,
):
    return models.Measurement(
        name=name,
        description=description,
        directory=directory,
        number_of_files=number_of_files,
        patient_reference=patient_reference,
        shifter_id=shifter_id,
        directory_id=measuerement_directory_id,
    )


@router.get("/")
def read_measurements(db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).all()


@router.post("/new")
def new_measurement(
    measurement_data: MeasurementBase,
    db: Session = Depends(get_session_local),
    _=Depends(get_current_user_with_role(Role.SHIFTER)),
):
    try:
        measurement = generate_measurement(
            name=measurement_data.name,
            description=measurement_data.description,
            directory=measurement_data.directory,
            number_of_files=measurement_data.number_of_files,
            patient_reference=measurement_data.patient_reference,
            shifter_id=measurement_data.shifter_id,
            measuerement_directory_id=measurement_data.measurement_folder_id,
        )
        db.add(measurement)
        db.commit()
        return {"message": "Measurement successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create measurement: {str(e)}"
        )


@router.get("/{id}")
def read_measurement(id: str, db: Session = Depends(get_session_local)):
    measurement = (
        db.query(models.Measurement)
        .filter(models.Measurement.id == id)
        .options(
            joinedload(models.Measurement.tags),
            joinedload(models.Measurement.radioisotopes),
            joinedload(models.Measurement.data_entry),
        )
        .first()
    )

    logger.debug(measurement)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    comments = (
        db.query(models.Comment)
        .filter(models.Comment.measurement_id == id)
        .options(
            joinedload(models.Comment.user),
            joinedload(models.Comment.comment_pictures),
        )
        .order_by(models.Comment.created_at.asc())
        .all()
    )

    logger.debug(comments)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append(
            {
                "id": comment.id,
                "content": comment.content,
                "user": comment.user,
                "measurement_id": comment.measurement_id,
                "created_at": str(comment.created_at),
                "pictures": [
                    CommentPictureResponse.from_orm(pic)
                    for pic in comment.comment_pictures
                ],
            }
        )

    return {
        "id": measurement.id,
        "name": measurement.name,
        "description": measurement.description,
        "directory": measurement.directory_id,
        "number_of_files": measurement.number_of_files,
        "patient_reference": measurement.patient_reference,
        "shifter_id": measurement.shifter_id,
        "tags": measurement.tags,
        "radioisotopes": measurement.radioisotopes,
        "data_entry": measurement.data_entry,
        "comments": serialized_comments,
    }


@router.post("/{id}/comments")
async def add_measurement_comment(
    id: str,
    content: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_session_local),
    user: models.User = Depends(get_current_user),
):
    measurement = (
        db.query(models.Measurement)
        .filter(models.Measurement.id == id)
        .first()
    )
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    new_comment = models.Comment(
        content=content,
        measurement_id=measurement.id,
        user_id=user["id"],
    )
    db.add(new_comment)
    db.commit()

    await save_comment_pictures(files, new_comment.id, db)

    db.refresh(new_comment)

    return {
        "message": "Comment added successfully",
        "comment": {
            "id": new_comment.id,
            "content": new_comment.content,
            "user": new_comment.user,
            "measurement_id": new_comment.measurement_id,
            "created_at": str(new_comment.created_at),
            "pictures": [
                CommentPictureResponse.from_orm(pic)
                for pic in new_comment.comment_pictures
            ],
        },
    }


@router.patch("/{measurement_id}/comments/{comment_id}")
async def edit_measurement_comment(
    measurement_id: str,
    comment_id: int,
    content: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    deleted_picture_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_session_local),
    user: models.User = Depends(get_current_user),
):
    measurement = (
        db.query(models.Measurement)
        .filter(models.Measurement.id == measurement_id)
        .first()
    )
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    comment = (
        db.query(models.Comment)
        .filter(
            models.Comment.id == comment_id,
            models.Comment.measurement_id == measurement_id,
            models.Comment.user_id == user["id"],
        )
        .first()
    )
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found or you do not have permission to edit it.",
        )

    comment.content = content
    db.commit()  # Commit the content update

    if deleted_picture_ids:
        for pic_id in deleted_picture_ids:
            pic = (
                db.query(models.CommentPicture)
                .filter(
                    models.CommentPicture.id == int(pic_id),
                    models.CommentPicture.comment_id == comment.id,
                )
                .first()
            )
            if pic:
                db.delete(pic)
        db.commit()

    await save_comment_pictures(files, comment.id, db)

    db.refresh(comment)

    return {
        "message": "Comment updated successfully",
        "comment": {
            "id": comment.id,
            "content": comment.content,
            "user": comment.user,
            "measurement_id": comment.measurement_id,
            "created_at": str(comment.created_at),
            "pictures": [
                CommentPictureResponse.from_orm(pic)
                for pic in comment.comment_pictures
            ],
        },
    }


async def save_comment_pictures(files, comment_id, db):
    os.makedirs(PICTURES_DIR, exist_ok=True)
    if files:
        for file in files:
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{file.filename}' is not an image.",
                )
            ext = os.path.splitext(file.filename)[1]
            filename = f"{comment_id}_{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(PICTURES_DIR, filename)
            with open(file_path, "wb") as f:
                content_bytes = await file.read()
                f.write(content_bytes)
            picture_url = f"/static/pictures/{filename}"
            picture = models.CommentPicture(
                path=picture_url, comment_id=comment_id
            )
            db.add(picture)
        db.commit()


@router.delete("/{measurement_id}/comments/{comment_id}")
def delete_measurement_comment(
    measurement_id: str,
    comment_id: int,
    db: Session = Depends(get_session_local),
    user: models.User = Depends(get_current_user),
):
    measurement = (
        db.query(models.Measurement)
        .filter(models.Measurement.id == measurement_id)
        .first()
    )
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    comment = (
        db.query(models.Comment)
        .filter(
            models.Comment.id == comment_id,
            models.Comment.measurement_id == measurement_id,
            models.Comment.user_id == user["id"],
        )
        .first()
    )
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found or you do not have permission to delete it.",
        )

    db.delete(comment)
    db.commit()
    return


@router.patch("/{id}/edit")
def edit_measurement(
    id: str,
    measurement_data: MeasurementBase,
    db: Session = Depends(get_session_local),
    _=Depends(get_current_user_with_role(Role.SHIFTER)),
):
    try:
        measurement = (
            db.query(models.Measurement)
            .filter(models.Measurement.id == id)
            .first()
        )
        if not measurement:
            raise HTTPException(
                status_code=404, detail="Measurement not found"
            )

        measurement.name = measurement_data.name
        measurement.description = measurement_data.description
        measurement.directory = measurement_data.directory
        measurement.number_of_files = measurement_data.number_of_files
        measurement.patient_reference = measurement_data.patient_reference
        measurement.shifter_id = measurement_data.shifter_id
        measurement.measurement_folder_id = (
            measurement_data.measurement_folder_id
        )

        db.commit()
        db.refresh(measurement)
        return {"message": "Measurement updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update measurement: {str(e)}"
        )


@router.post("/create_sample_measurements/")
def create_sample_measurements(
    db: Session = Depends(get_session_local),
    amount: int = 10,
    fake_data: dict = None,
):
    measurements = generate_models(
        models.Measurement, generate_fake_measurement, db, amount, fake_data
    )
    try:
        db.add_all(measurements)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create measurements"
        )
    return {"message": "Sample measurements created"}


@router.get("/{id}/histogram-data")
def get_filtered_histogram_data(
    id: str,
    start_time: Optional[datetime] = Query(
        None, description="Start datetime filter (ISO format)"
    ),
    end_time: Optional[datetime] = Query(
        None, description="End datetime filter (ISO format)"
    ),
    db: Session = Depends(get_session_local),
):
    measurement = (
        db.query(models.Measurement)
        .filter(models.Measurement.id == id)
        .first()
    )
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    try:
        aggregated_histograms = aggregate_histogram_data_sql(
            id, start_time, end_time, db
        )
    except Exception as e:
        print(f"SQL aggregation failed, falling back to Python: {e}")
        query = db.query(models.DataEntry).filter(
            models.DataEntry.measurement_id == id
        )

        if start_time:
            query = query.filter(
                models.DataEntry.acquisition_date >= start_time
            )
        if end_time:
            query = query.filter(models.DataEntry.acquisition_date <= end_time)

        data_entries = query.all()
        if not data_entries:
            return {
                "measurement": measurement,
                "data_entry": [],
                "total_entries_aggregated": 0,
                "date_range": {"start_time": start_time, "end_time": end_time},
            }
        aggregated_histograms = aggregate_histogram_data(data_entries)

    count_query = db.query(models.DataEntry).filter(
        models.DataEntry.measurement_id == id
    )
    if start_time:
        count_query = count_query.filter(
            models.DataEntry.acquisition_date >= start_time
        )
    if end_time:
        count_query = count_query.filter(
            models.DataEntry.acquisition_date <= end_time
        )

    total_entries = count_query.count()

    if total_entries == 0:
        return {
            "measurement": measurement,
            "data_entry": [],
            "total_entries_aggregated": 0,
            "date_range": {"start_time": start_time, "end_time": end_time},
        }

    # Get first entry for metadata
    first_entry = count_query.first()

    date_range_str = ""
    if start_time and end_time:
        date_range_str = f" ({start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')})"
    elif start_time:
        date_range_str = f" (from {start_time.strftime('%Y-%m-%d %H:%M')})"
    elif end_time:
        date_range_str = f" (until {end_time.strftime('%Y-%m-%d %H:%M')})"

    virtual_data_entry = {
        "id": f"normalized_{id}",
        "name": f"Normalized Data{date_range_str}",
        "data": aggregated_histograms,
        "acquisition_date": (
            first_entry.acquisition_date if first_entry else None
        ),
        "measurement_id": id,
        "histo_dir": first_entry.histo_dir if first_entry else "",
    }

    return {
        "measurement": measurement,
        "data_entry": [virtual_data_entry],
        "total_entries_aggregated": total_entries,
        "date_range": {"start_time": start_time, "end_time": end_time},
    }


def aggregate_histogram_data(data_entries):
    if not data_entries:
        return []

    first_entry_data = data_entries[0].data
    if not first_entry_data:
        return []

    num_histograms = len(first_entry_data)
    aggregated_histograms = []

    for hist_index in range(num_histograms):
        first_histogram = first_entry_data[hist_index]
        aggregated_hist = dict(first_histogram)

        if "y" in aggregated_hist and aggregated_hist["y"]:
            y_values = [first_histogram["y"]]

            for entry in data_entries[1:]:
                if (
                    entry.data
                    and len(entry.data) > hist_index
                    and "y" in entry.data[hist_index]
                ):
                    y_values.append(entry.data[hist_index]["y"])

            if y_values:
                aggregated_hist["y"] = [sum(vals) for vals in zip(*y_values)]

        if "content" in aggregated_hist and aggregated_hist["content"]:
            content_matrices = [first_histogram["content"]]

            for entry in data_entries[1:]:
                if (
                    entry.data
                    and len(entry.data) > hist_index
                    and "content" in entry.data[hist_index]
                ):
                    content_matrices.append(entry.data[hist_index]["content"])

            if content_matrices:
                aggregated_content = []
                for row_idx in range(len(content_matrices[0])):
                    row_values = [
                        matrix[row_idx] for matrix in content_matrices
                    ]
                    aggregated_row = [sum(vals) for vals in zip(*row_values)]
                    aggregated_content.append(aggregated_row)
                aggregated_hist["content"] = aggregated_content

        if "name" in aggregated_hist:
            aggregated_hist["name"] = f"Normalized {aggregated_hist['name']}"

        aggregated_histograms.append(aggregated_hist)

    return aggregated_histograms


def aggregate_histogram_data_sql(
    measurement_id: str,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    db: Session,
):
    """
    SQL-level histogram aggregation using PostgreSQL JSONB functions.
    More efficient for large datasets but requires PostgreSQL-specific features.
    """
    # Build the query with optional date filters
    base_query = """
    SELECT 
        jsonb_agg(
            jsonb_build_object(
                'id', de.id,
                'name', de.name,
                'acquisition_date', de.acquisition_date,
                'data', de.data
            )
        ) as data_entries
    FROM data_entry de 
    WHERE de.measurement_id = :measurement_id
    """

    params = {"measurement_id": measurement_id}

    if start_time:
        base_query += " AND de.acquisition_date >= :start_time"
        params["start_time"] = start_time

    if end_time:
        base_query += " AND de.acquisition_date <= :end_time"
        params["end_time"] = end_time

    result = db.execute(text(base_query), params).fetchone()

    if not result or not result.data_entries:
        return []

    data_entries_data = result.data_entries

    from types import SimpleNamespace

    mock_entries = []
    for entry_data in data_entries_data:
        mock_entry = SimpleNamespace()
        mock_entry.data = entry_data["data"]
        mock_entries.append(mock_entry)

    return aggregate_histogram_data(mock_entries)
