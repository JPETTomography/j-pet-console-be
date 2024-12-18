from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload, load_only
import database.models as models
from database.database import get_session_local
from backend.utills.utills import get_random_user, get_random_detector
from backend.routers.common import generate_models
import random
import faker
from datetime import timedelta

generator = faker.Faker()
router = APIRouter()

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
    return db.query(models.Experiment).filter(models.Experiment.id == id).first() or f"No experiment with id: {id} found."

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
