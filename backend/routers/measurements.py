from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import os
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.routers.common import generate_models
import database.models as models
from database.database import get_session_local
from backend.auth import get_current_user_with_role, Role, get_current_user
from sqlalchemy import func
from backend.utills.utills import (
    get_random_user,
    get_random_tags,
    get_random_radioisotopes,
)
import faker
import random
import uuid

PICTURES_DIR = os.environ.get("PICTURES_DIR", "pictures")

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])


class MeasurementBase(BaseModel):
    name: str = Field(..., example="Measurement Name")
    description: str = Field(..., example="A detailed description of the measurement")
    directory: str = Field(..., example="/path/to/directory")
    number_of_files: int = Field(..., example=5)
    patient_reference: str = Field(..., example="Patient Reference")
    shifter_id: int = Field(..., example=1)
    experiment_id: int = Field(..., example=1)


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
    all_experiments = db.query(models.Experiment.id).order_by(func.random())
    experiments_list = [exp.id for exp in all_experiments]
    experiments_list_size = len(experiments_list)
    i = 0
    while True:
        experiment_id = experiments_list[i % experiments_list_size]
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            directory="/".join(
                [generator.catch_phrase().partition(" ")[0] for _ in range(2)]
            ),
            number_of_files=random.randint(1, 10),
            patient_reference=generator.text(max_nb_chars=200),
            shifter_id=get_random_user(db).id,
            experiment_id=experiment_id,
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
    experiment_id: int,
):
    return models.Measurement(
        name=name,
        description=description,
        directory=directory,
        number_of_files=number_of_files,
        patient_reference=patient_reference,
        shifter_id=shifter_id,
        experiment_id=experiment_id,
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
            experiment_id=measurement_data.experiment_id,
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
        "directory": measurement.directory,
        "number_of_files": measurement.number_of_files,
        "patient_reference": measurement.patient_reference,
        "shifter_id": measurement.shifter_id,
        "experiment_id": measurement.experiment_id,
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
        db.query(models.Measurement).filter(models.Measurement.id == id).first()
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
                CommentPictureResponse.from_orm(pic) for pic in comment.comment_pictures
            ],
        },
    }


async def save_comment_pictures(files, comment_id, db):
    os.makedirs(PICTURES_DIR, exist_ok=True)
    if files:
        for file in files:
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail=f"File '{file.filename}' is not an image."
                )
            ext = os.path.splitext(file.filename)[1]
            filename = f"{comment_id}_{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(PICTURES_DIR, filename)
            with open(file_path, "wb") as f:
                content_bytes = await file.read()
                f.write(content_bytes)
            picture_url = f"/static/pictures/{filename}"
            picture = models.CommentPicture(path=picture_url, comment_id=comment_id)
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
            db.query(models.Measurement).filter(models.Measurement.id == id).first()
        )
        if not measurement:
            raise HTTPException(status_code=404, detail="Measurement not found")

        measurement.name = measurement_data.name
        measurement.description = measurement_data.description
        measurement.directory = measurement_data.directory
        measurement.number_of_files = measurement_data.number_of_files
        measurement.patient_reference = measurement_data.patient_reference
        measurement.shifter_id = measurement_data.shifter_id
        measurement.experiment_id = measurement_data.experiment_id

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
    db: Session = Depends(get_session_local), amount: int = 10, fake_data: dict = None
):
    measurements = generate_models(
        models.Measurement, generate_fake_measurement, db, amount, fake_data
    )
    try:
        db.add_all(measurements)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create measurements")
    return {"message": "Sample measurements created"}
