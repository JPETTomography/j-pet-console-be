from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import database.models as models
from database.database import get_session_local
from backend.routers.common import generate_models
from sqlalchemy import func
from backend.utills.utills import get_random_user, get_random_experiment, get_random_tags, get_random_radioisotopes
import faker
import random

generator = faker.Faker()
router = APIRouter()

def generate_fake_measurement(db: Session=None):
    all_experiments = db.query(models.Experiment.id).order_by(func.random())
    experiments_list = [exp.id for exp in all_experiments]
    experiments_list_size = len(experiments_list)
    i = 0
    while True:
        experiment_id = experiments_list[i % experiments_list_size]
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            directory="/".join([generator.catch_phrase().partition(" ")[0] for _ in range(2)]),
            number_of_files=random.randint(1, 10),
            patient_reference=generator.text(max_nb_chars=200),
            shifter_id=get_random_user(db).id,
            experiment_id=experiment_id,
            tags=get_random_tags(db, random.randint(0, 2)),
            radioisotopes=get_random_radioisotopes(db, random.randint(0, 2))
        )
        i += 1


@router.get("/")
def read_measurements(db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).all()

@router.get("/{id}")
def read_measurement(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).filter(models.Measurement.id == id).options(joinedload(models.Measurement.tags),
                                                                                    joinedload(models.Measurement.radioisotopes)).first()

@router.post("/create_sample_measurements/")
# @TODO remove this later
def create_sample_measurements(db: Session = Depends(get_session_local), amount: int = 10, fake_data:dict=None):
    measurements = generate_models(models.Measurement, generate_fake_measurement, db, amount, fake_data)
    try:
        db.add_all(measurements)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create measurements")
    return {"message": "Sample measurements created"}
