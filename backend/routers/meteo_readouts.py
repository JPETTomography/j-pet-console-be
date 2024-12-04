from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_meteo_readout

router = APIRouter()

@router.get("/")
def read_meteo_readouts(db: Session = Depends(get_session_local)):
    return db.query(models.MeteoReadout).all()

@router.get("/{id}")
def read_meteo_readout(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.MeteoReadout).filter(models.MeteoReadout.id == id).first() or f"No meteo readout with {id} id has been found."

@router.post("/create_sample_meteo_readouts/")
# @TODO remove this later
def create_sample_meteo_readouts(db: Session = Depends(get_session_local), amount: int = 10):
    meteo_readouts = [generate_fake_meteo_readout(db) for _ in range(amount)]
    try:
        db.add_all(meteo_readouts)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create meteo_readouts")
    return {"message": "Sample meteo readouts created"}
