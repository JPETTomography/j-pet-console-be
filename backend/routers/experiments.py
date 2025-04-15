from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload, load_only, joinedload
import database.models as models
from database.database import get_session_local
from backend.auth import get_current_user
from backend.utills.utills import get_random_user, get_random_detector
from backend.routers.common import generate_models
from typing import List
import random
import faker
from datetime import timedelta

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])

def generate_fake_experiment(db: Session=None):
    i = 0
    detector_ids = [d.id for d in db.query(models.Detector.id).distinct().all()]
    sd_size = len(detector_ids)
    while True:
        start_date = generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None)
        end_date = random.choice([start_date + timedelta(days=random.randint(1, 30)), None])
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            status=random.choice(["draft", "ongoing", "closed", "archived"]),
            location=generator.city(),
            start_date=start_date,
            end_date=end_date,
            coordinator_id=get_random_user(db).id,
            detector_id=detector_ids[i%sd_size]
        )
        i+=1

@router.get("/")
def read_experiments(db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).options(selectinload(models.Experiment.coordinator).load_only(models.User.name)).all()

@router.get("/{id}")
def read_experiment(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).filter(models.Experiment.id == id).options(selectinload(models.Experiment.coordinator).load_only(models.User.name)).first() or f"No experiment with id: {id} found."

@router.get("/{id}/measurements")
def read_experiment_measurements(
        id: str,
        db: Session = Depends(get_session_local),
        page: int = Query(1, ge=1),
        size: int = Query(10, le=10)
):
    offset = (page - 1) * size
    measurements = db.query(models.Measurement).filter(models.Measurement.experiment_id == id)
    measurements = measurements.options(joinedload(models.Measurement.tags)).limit(size).offset(offset).all()
    if not measurements:
        raise HTTPException(status_code=404, detail=f"No measurements found for experiment with id: {id}")
    return measurements

@router.post("/create_sample_experiments/")
# @TODO remove this later
def create_sample_experiments(db: Session = Depends(get_session_local), amount: int = 10, fake_data:dict=None):
    experiments = generate_models(models.Experiment, generate_fake_experiment, db, amount, fake_data)
    try:
        db.add_all(experiments)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create experiments")
    return {"message": "Sample experiments created"}
