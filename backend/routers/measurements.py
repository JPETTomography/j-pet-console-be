from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session, joinedload
import database.models as models
from database.database import get_session_local
from backend.auth import verify_access_token
from backend.routers.common import generate_models
from sqlalchemy import func
from backend.utills.utills import get_random_user, get_random_experiment, get_random_tags, get_random_radioisotopes
import faker
import random

generator = faker.Faker()
router = APIRouter()

PERMITTED_ROLE = "shifter"

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

def generate_measurement(name: str, description: str, directory: str, number_of_files: int, patient_reference: str, shifter_id: int, experiment_id: int):
    return models.Measurement(
        name=name,
        description=description,
        directory=directory,
        number_of_files=number_of_files,
        patient_reference=patient_reference,
        shifter_id=shifter_id,
        experiment_id=experiment_id
    )

@router.get("/")
def read_measurements(db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).all()

@router.post("/new")
def new_measurement(name: str = Form(...), description: str = Form(...), directory: str = Form(...), number_of_files: int = Form(...),
                   patient_reference: str = Form(...), shifter_id: int = Form(...), experiment_id: int = Form(...),
                   token: str = Form(...), db: Session = Depends(get_session_local)):
    try:
        verify_access_token(token, PERMITTED_ROLE, db)

        measurement = generate_measurement(name=name, description=description, directory=directory, number_of_files=number_of_files,
                                           patient_reference=patient_reference, shifter_id=shifter_id, experiment_id=experiment_id)

        db.add(measurement)
        db.commit()
        return {"message": "Measurement successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create measurement: {str(e)}")

@router.get("/{id}")
def read_measurement(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).filter(models.Measurement.id == id).options(joinedload(models.Measurement.tags),
                                                                                    joinedload(models.Measurement.radioisotopes),
                                                                                    joinedload(models.Measurement.data_entry)).first()
@router.patch("/{id}/edit")
def edit_measurement(id: str, name: str = Form(...), description: str = Form(...), directory: str = Form(...), number_of_files: int = Form(...),
                     patient_reference: str = Form(...), shifter_id: int = Form(...),
                     token: str = Form(...), db: Session = Depends(get_session_local)):
    try:
        verify_access_token(token, PERMITTED_ROLE, db)

        measurement = db.query(models.Measurement).filter(models.Measurement.id == id).first()
        if not measurement:
            raise HTTPException(status_code=404, detail="Measurement not found")

        measurement.name = name
        measurement.description = description
        measurement.directory = directory
        measurement.number_of_files = number_of_files
        measurement.patient_reference = patient_reference
        measurement.shifter_id = shifter_id

        db.commit()
        db.refresh(measurement)
        return {"message": "Measurement updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update measurement: {str(e)}")

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
