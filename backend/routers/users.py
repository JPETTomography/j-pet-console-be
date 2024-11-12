from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_user
router = APIRouter()

@router.get("/")
def read_users(db: Session = Depends(get_session_local)):
    return db.query(models.User).all()

@router.get("/{id}")
def read_user(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.User).filter(models.User.id == id).first() or f"No user with id: {id} found."

@router.post("/create_sample_users/")
# @TODO remove this later
def create_sample_users(db: Session = Depends(get_session_local), amount: int = 10):
    users = [generate_fake_user() for _ in range(amount)]
    db.add_all(users)
    db.commit()
    return {"message": "Sample users created"}
