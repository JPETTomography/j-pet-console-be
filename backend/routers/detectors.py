from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_detector

router = APIRouter()

@router.get("/")
def read_detectors(db: Session = Depends(get_session_local)):
    return db.query(models.Detector).all()

@router.get("/{id}")
def read_detector(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Detector).filter(models.Detector.id == id).first() or f"No detector with {id} id has been found."

@router.post("/create_sample_detectors/")
# @TODO remove this later
def create_sample_detectors(db: Session = Depends(get_session_local), amount: int = 10):
    detectors = [generate_fake_detector() for _ in range(amount)]
    try:
        db.add_all(detectors)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create detectors")
    return {"message": "Sample detectors created"}
