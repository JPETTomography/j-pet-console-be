from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field
import database.models as models
from database.database import get_session_local
from backend.auth import get_current_user_with_role, Role, get_current_user
from sqlalchemy import func
from backend.utills.utills import get_random_user, get_random_tags, get_random_radioisotopes
import faker
import random

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])


# Measurement base model
class MeasurementBase(BaseModel):
    name: str = Field(..., example="Measurement Name")
    description: str = Field(..., example="A detailed description of the measurement")
    directory: str = Field(..., example="/path/to/directory")
    number_of_files: int = Field(..., example=5)
    patient_reference: str = Field(..., example="Patient Reference")
    shifter_id: int = Field(..., example=1)
    experiment_id: int = Field(..., example=1)


# Generate fake data for testing
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


# CRUD endpoints for measurements
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
        .options(joinedload(models.Comment.user))
        .order_by(models.Comment.created_at.asc())
        .all()
    )

    measurement.comments = comments

    return measurement


class CommentRequest(BaseModel):
    content: str


@router.post("/{id}/comments")
def add_measurement_comment(
    id: str,
    comment_request: CommentRequest,
    db: Session = Depends(get_session_local),
    user: models.User = Depends(get_current_user)
):
    measurement = db.query(models.Measurement).filter(models.Measurement.id == id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    new_comment = models.Comment(
        content=comment_request.content,
        measurement_id=measurement.id,
        user_id=user["id"]
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "message": "Comment added successfully",
        "comment": {
            "id": new_comment.id,
            "content": new_comment.content,
            "user": new_comment.user,
            "measurement_id": new_comment.measurement_id,
            "created_at": new_comment.created_at
        }
    }


# Edit comment endpoint
class CommentEditRequest(BaseModel):
    content: str


@router.patch("/{measurement_id}/comments/{comment_id}")
def edit_measurement_comment(
    measurement_id: str,
    comment_id: int,
    comment_data: CommentEditRequest,
    db: Session = Depends(get_session_local),
    user: models.User = Depends(get_current_user)
):
    measurement = db.query(models.Measurement).filter(models.Measurement.id == measurement_id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    comment = (
        db.query(models.Comment)
        .filter(
            models.Comment.id == comment_id,
            models.Comment.measurement_id == measurement_id,
            models.Comment.user_id == user["id"]
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or you do not have permission to edit it.")

    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    return {
        "message": "Comment updated successfully",
        "comment": {
            "id": comment.id,
            "content": comment.content,
            "user": comment.user,
            "measurement_id": comment.measurement_id,
            "created_at": comment.created_at
        }
    }


# Delete comment endpoint
@router.delete("/{measurement_id}/comments/{comment_id}")
def delete_measurement_comment(
    measurement_id: str,
    comment_id: int,
    db: Session = Depends(get_session_local),
    user: models.User = Depends(get_current_user)
):
    measurement = db.query(models.Measurement).filter(models.Measurement.id == measurement_id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    comment = (
        db.query(models.Comment)
        .filter(
            models.Comment.id == comment_id,
            models.Comment.measurement_id == measurement_id,
            models.Comment.user_id == user["id"]
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or you do not have permission to delete it.")

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
