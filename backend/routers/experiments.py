import json
import random
from datetime import datetime, timedelta
from typing import Optional

import faker
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload, selectinload

import database.models as models
from backend.auth import Role, get_current_user, get_current_user_with_role
from backend.routers.common import generate_models
from backend.utills.utills import get_random_user
from database.database import get_session_local

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])


class ExperimentBase(BaseModel):
    name: str = Field(..., example="Experiment Name")
    description: str = Field(
        ..., example="A detailed description of the experiment"
    )
    status: str = Field(..., example="draft")
    location: str = Field(..., example="New York")
    start_date: datetime = Field(..., example="2023-01-01T00:00:00")
    end_date: Optional[datetime] = Field(None, example="2023-01-31T00:00:00")
    coordinator_id: int = Field(..., example=1)
    detector_id: int = Field(..., example=1)


class ExperimentWithReference(ExperimentBase):
    reference_data: Optional[dict] = Field(
        None, example={"reference_plots": []}
    )


def generate_fake_experiment(db: Session = None):
    i = 0
    detector_ids = [
        d.id for d in db.query(models.Detector.id).distinct().all()
    ]
    sd_size = len(detector_ids)
    while True:
        start_date = generator.date_time_this_year(
            before_now=True, after_now=False, tzinfo=None
        )
        end_date = random.choice(
            [start_date + timedelta(days=random.randint(1, 30)), None]
        )
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            status=random.choice(["draft", "ongoing", "closed", "archived"]),
            location=generator.city(),
            start_date=start_date,
            end_date=end_date,
            coordinator_id=get_random_user(db).id,
            detector_id=detector_ids[i % sd_size],
        )
        i += 1


def generate_experiment(
    name: str,
    description: str,
    status: str,
    location: str,
    coordinator_id: int,
    detector_id: int,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    reference_data: Optional[dict] = None,
):
    return models.Experiment(
        name=name,
        description=description,
        status=status,
        location=location,
        start_date=start_date,
        end_date=end_date,
        coordinator_id=coordinator_id,
        detector_id=detector_id,
        reference_data=reference_data,
    )


@router.get("/")
def read_experiments(db: Session = Depends(get_session_local)):
    return (
        db.query(models.Experiment)
        .options(
            selectinload(models.Experiment.coordinator).load_only(
                models.User.name
            )
        )
        .all()
    )


@router.post("/new")
def new_experiment(
    experiment_data: ExperimentBase,
    db: Session = Depends(get_session_local),
    _=Depends(get_current_user_with_role(Role.COORDINATOR)),
):
    try:
        experiment = generate_experiment(
            name=experiment_data.name,
            description=experiment_data.description,
            status=experiment_data.status,
            location=experiment_data.location,
            start_date=experiment_data.start_date,
            end_date=experiment_data.end_date,
            coordinator_id=experiment_data.coordinator_id,
            detector_id=experiment_data.detector_id,
        )
        db.add(experiment)
        db.commit()
        return {"message": "Experiment successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create experiment: {str(e)}"
        )


@router.get("/{id}")
def read_experiment(id: str, db: Session = Depends(get_session_local)):
    return (
        db.query(models.Experiment)
        .filter(models.Experiment.id == id)
        .options(
            selectinload(models.Experiment.coordinator).load_only(
                models.User.name
            )
        )
        .first()
        or f"No experiment with id: {id} found."
    )


@router.patch("/{id}/edit")
def edit_experiment(
    id: str,
    experiment_data: ExperimentWithReference,
    db: Session = Depends(get_session_local),
    _=Depends(get_current_user_with_role(Role.COORDINATOR)),
):
    try:
        experiment = (
            db.query(models.Experiment)
            .filter(models.Experiment.id == id)
            .first()
        )
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")

        # Update fields
        experiment.name = experiment_data.name
        experiment.description = experiment_data.description
        experiment.status = experiment_data.status
        experiment.location = experiment_data.location
        experiment.start_date = experiment_data.start_date
        experiment.end_date = experiment_data.end_date
        experiment.coordinator_id = experiment_data.coordinator_id
        experiment.detector_id = experiment_data.detector_id

        if experiment_data.reference_data is not None:
            experiment.reference_data = experiment_data.reference_data

        db.commit()
        db.refresh(experiment)
        return {"message": "Experiment updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update experiment: {str(e)}"
        )


@router.get("/{id}/measurements")
def read_experiment_measurements(
    id: str,
    db: Session = Depends(get_session_local),
    page: int = Query(1, ge=1),
    size: int = Query(10, le=10),
):
    # First check if experiment exists
    experiment = (
        db.query(models.Experiment).filter(models.Experiment.id == id).first()
    )
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id: {id} not found",
        )

    offset = (page - 1) * size
    measurements = db.query(models.Measurement).filter(
        models.Measurement.experiment_id == id
    )
    measurements = (
        measurements.options(joinedload(models.Measurement.tags))
        .limit(size)
        .offset(offset)
        .all()
    )

    # Return empty list if no measurements found, don't raise 404
    return measurements


@router.post("/create_sample_experiments/")
# @TODO remove this later
def create_sample_experiments(
    db: Session = Depends(get_session_local),
    amount: int = 10,
    fake_data: dict = None,
):
    experiments = generate_models(
        models.Experiment, generate_fake_experiment, db, amount, fake_data
    )
    try:
        db.add_all(experiments)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create experiments"
        )
    return {"message": "Sample experiments created"}


@router.post("/{id}/upload-reference-data")
async def upload_reference_data(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_session_local),
    _=Depends(get_current_user_with_role(Role.COORDINATOR)),
):
    try:
        experiment = (
            db.query(models.Experiment)
            .filter(models.Experiment.id == id)
            .first()
        )
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")

        if not file.filename.endswith(".json"):
            raise HTTPException(
                status_code=400, detail="File must be a JSON file"
            )

        content = await file.read()
        try:
            reference_data = json.loads(content.decode("utf-8"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        if not isinstance(reference_data, dict):
            raise HTTPException(
                status_code=400, detail="Reference data must be a JSON object"
            )

        experiment.reference_data = reference_data
        db.commit()
        db.refresh(experiment)

        return {
            "message": "Reference data uploaded successfully",
            "filename": file.filename,
            "data_keys": (
                list(reference_data.keys())
                if isinstance(reference_data, dict)
                else []
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload reference data: {str(e)}",
        )


@router.get("/{id}/reference-data")
def get_reference_data(id: str, db: Session = Depends(get_session_local)):
    experiment = (
        db.query(models.Experiment).filter(models.Experiment.id == id).first()
    )
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {
        "experiment_id": experiment.id,
        "reference_data": experiment.reference_data,
    }
