from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload, load_only, joinedload
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_experiment

router = APIRouter()

@router.get("/")
def read_experiments(db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).options(selectinload(models.Experiment.coordinator).load_only(models.User.name)).all()

@router.get("/{id}")
def read_experiment(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).filter(models.Experiment.id == id).first() or f"No experiment with id: {id} found."

@router.get("/{id}/measurements")
def read_experiment_measurements(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Measurement).filter(models.Measurement.experiment_id == id).options(joinedload(models.Measurement.tags)).all()

@router.post("/create_sample_experiments/")
# @TODO remove this later
def create_sample_experiments(db: Session = Depends(get_session_local), amount: int = 10):
    experiments = [generate_fake_experiment(db) for _ in range(amount)]
    try:
        db.add_all(experiments)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create experiments")
    return {"message": "Sample experiments created"}
