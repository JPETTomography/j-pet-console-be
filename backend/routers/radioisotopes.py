from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.routers.common import generate_models
import faker
import random

generator = faker.Faker()
router = APIRouter()


def generate_fake_radioisotope(db: Session=None):
    while True:
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            activity=float(random.random()),
            halflife=float(random.random())
        )

@router.get("/")
def read_radioisotopes(db: Session = Depends(get_session_local)):
    return db.query(models.Radioisotope).all()

@router.get("/{id}")
def read_radioisotope(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Radioisotope).filter(models.Radioisotope.id == id).first() or f"No radioisotope with id: {id} found."

@router.post("/create_sample_radioisotopes/")
# @TODO remove this later
def create_sample_radioisotopes(db: Session = Depends(get_session_local), amount: int = 10, fake_data:dict=None):
    radioisotopes = generate_models(models.Radioisotope, generate_fake_radioisotope, db, amount, fake_data)
    try:
        db.add_all(radioisotopes)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create radioisotopes")
    return {"message": "Sample radioisotopes created"}
