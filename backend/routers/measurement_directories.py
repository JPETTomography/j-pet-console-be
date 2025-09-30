import faker
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

import database.models as models
from backend.auth import get_current_user
from backend.routers.common import generate_models
from backend.utills.utills import get_random_experiment, get_random_measurement
from database.database import get_session_local

generator = faker.Faker()

router = APIRouter(dependencies=[Depends(get_current_user)])


def generate_fake_measurement_directory(db: Session = None):
    all_experiments = db.query(models.Experiment.id).order_by(func.random())
    experiments_list = [exp.id for exp in all_experiments]
    experiments_list_size = len(experiments_list)
    i = 0
    while True:
        experiment_id = experiments_list[i % experiments_list_size]
        yield dict(
            path=generator.file_path(extension=[]),
            available=True,
            created_at=generator.date_time_this_year(
                before_now=True, after_now=False, tzinfo=None
            ),
            experiment_id=experiment_id,
        )
        i += 1


@router.post("/create_sample_measurement_directories/")
def create_sample_measurement_directories(
    db: Session = Depends(get_session_local),
    amount: int = 2,
    fake_data: dict = None,
):
    measurement_dirs = generate_models(
        models.MeasurementDirectory,
        generate_fake_measurement_directory,
        db,
        amount,
        fake_data,
    )
    try:
        db.add_all(measurement_dirs)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create measurements"
        )
    return {"message": "Sample measurements created"}


@router.get("/")
def read_measurement_directoreis(db: Session = Depends(get_session_local)):
    return db.query(models.MeasurementDirectory).all()
