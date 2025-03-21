from fastapi import APIRouter, Depends, HTTPException, Form, Query
from typing import Optional
from sqlalchemy.orm import Session, selectinload, load_only, joinedload
import database.models as models
from backend.auth import verify_access_token
from database.database import get_session_local
from backend.auth import get_current_user
from backend.utills.utills import get_random_user, get_random_detector
from backend.routers.common import generate_models
from typing import List
import random
import faker
from datetime import timedelta, datetime

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])

PERMITTED_ROLE = "coordinator"

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

def generate_experiment(name: str, description: str, status: str, location: str, coordinator_id: int, detector_id: int, start_date: datetime, end_date: Optional[datetime] = None):
    return models.Experiment(
        name=name,
        description=description,
        status=status,
        location=location,
        start_date=start_date,
        end_date=end_date,
        coordinator_id=coordinator_id,
        detector_id=detector_id
    )

@router.get("/")
def read_experiments(db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).options(selectinload(models.Experiment.coordinator).load_only(models.User.name)).all()

@router.post("/new")
def new_experiment(name: str = Form(...), description: str = Form(...), status: str = Form(...), location: str = Form(...),
                   start_date: str = Form(...), end_date: Optional[str] = Form(None), coordinator_id: int = Form(...), detector_id: int = Form(...),
                   token: str = Form(...), db: Session = Depends(get_session_local)):
    try:
        verify_access_token(token, PERMITTED_ROLE, db)

        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date) if bool(end_date) else None
        experiment = generate_experiment(name=name, description=description, status=status, location=location,
                                         start_date=start_date, end_date=end_date, coordinator_id=coordinator_id,
                                         detector_id=detector_id)

        db.add(experiment)
        db.commit()
        return {"message": "Experiment successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create experiment: {str(e)}")

@router.get("/{id}")
def read_experiment(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).filter(models.Experiment.id == id).options(selectinload(models.Experiment.coordinator).load_only(models.User.name)).first() or f"No experiment with id: {id} found."

@router.patch("/{id}/edit")
def edit_experiment(id: str, name: str = Form(...), description: str = Form(...), status: str = Form(...), location: str = Form(...),
                   start_date: str = Form(...), end_date: Optional[str] = Form(None), coordinator_id: int = Form(...), detector_id: int = Form(...),
                   token: str = Form(...), db: Session = Depends(get_session_local)):
    try:
        verify_access_token(token, PERMITTED_ROLE, db)

        experiment = db.query(models.Experiment).filter(models.Experiment.id == id).first()
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")

        experiment.name = name
        experiment.description = description
        experiment.status = status
        experiment.location = location
        experiment.start_date = datetime.fromisoformat(start_date)
        experiment.end_date = datetime.fromisoformat(end_date) if bool(end_date) else None
        experiment.coordinator_id = coordinator_id
        experiment.detector_id = detector_id

        db.commit()
        db.refresh(experiment)
        return {"message": "Experiment updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update experiment: {str(e)}")

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
