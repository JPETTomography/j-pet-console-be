from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_measurement

router = APIRouter()

@router.get("/")
def read_measurements(db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).all()

@router.get("/{id}")
def read_measurement(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).filter(models.Measurement.id == id).first() or f"No measurement with id: {id} found."

@router.post("/create_sample_measurements/")
# @TODO remove this later
def create_sample_measurements(db: Session = Depends(get_session_local), amount: int = 10):
    measurements = [generate_fake_measurement(db) for _ in range(amount)]
    try:
        db.add_all(measurements)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create measurements")
    return {"message": "Sample measurements created"}
