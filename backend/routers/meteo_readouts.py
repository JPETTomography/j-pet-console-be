from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import get_random_measurement
from backend.routers.common import generate_models
import faker
import random

generator = faker.Faker()

router = APIRouter()


def generate_fake_meteo_readout(db: Session=None):
    while True:
        yield dict(
            station_time=generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
            agent_time=generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
            p_atm=float(random.random()),
            p_1=float(random.random()),
            p_2=float(random.random()),
            hum_1=float(random.random()),
            hum_2=float(random.random()),
            temp_1=float(random.random()),
            temp_2=float(random.random()),
            measurement_id=get_random_measurement(db).id
        )

@router.get("/")
def read_meteo_readouts(db: Session = Depends(get_session_local)):
    return db.query(models.MeteoReadout).all()

@router.get("/{id}")
def read_meteo_readout(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.MeteoReadout).filter(models.MeteoReadout.id == id).first() or f"No meteo readout with {id} id has been found."

@router.post("/create_sample_meteo_readouts/")
# @TODO remove this later
def create_sample_meteo_readouts(db: Session = Depends(get_session_local), amount: int = 10, fake_data:dict=None):
    meteo_readouts = generate_models(models.MeteoReadout, generate_fake_meteo_readout, db, amount, fake_data)
    try:
        db.add_all(meteo_readouts)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create meteo_readouts")
    return {"message": "Sample meteo readouts created"}
