from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload, load_only
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_experiment

router = APIRouter()

@router.get("/")
def read_experiments(db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).options(selectinload(models.Experiment.owner).load_only(models.User.name)).all()

@router.get("/{id}")
def read_experiment(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Experiment).filter(models.Experiment.id == id).first() or f"No experiment with id: {id} found."

@router.post("/create_sample_experiments/")
# @TODO remove this later
def create_sample_experiments(db: Session = Depends(get_session_local), amount: int = 10):
    experiments = [generate_fake_experiment(db) for _ in range(amount)]
    db.add_all(experiments)
    db.commit()
    return {"message": "Sample experiments created"}
