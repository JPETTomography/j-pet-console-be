from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_tag

router = APIRouter()

@router.get("/")
def read_tags(db: Session = Depends(get_session_local)):
    return db.query(models.Tag).all()

@router.get("/{id}")
def read_tag(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Tag).filter(models.Tag.id == id).first() or f"No tag with {id} id has been found."

@router.post("/create_sample_tags/")
# @TODO remove this later
def create_sample_tags(db: Session = Depends(get_session_local), amount: int = 10):
    tags = [generate_fake_tag() for _ in range(amount)]
    db.add_all(tags)
    db.commit()
    return {"message": "Sample tags created"}
