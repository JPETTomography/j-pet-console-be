from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_radioisotope

router = APIRouter()

@router.get("/")
def read_radioisotopes(db: Session = Depends(get_session_local)):
    return db.query(models.Radioisotope).all()

@router.get("/{id}")
def read_radioisotope(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Radioisotope).filter(models.Radioisotope.id == id).first() or f"No radioisotope with id: {id} found."

@router.post("/create_sample_radioisotopes/")
# @TODO remove this later
def create_sample_radioisotopes(db: Session = Depends(get_session_local), amount: int = 10):
    radioisotopes = [generate_fake_radioisotope() for _ in range(amount)]
    db.add_all(radioisotopes)
    db.commit()
    return {"message": "Sample radioisotopes created"}
