from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_document

router = APIRouter()

@router.get("/")
def read_documents(db: Session = Depends(get_session_local)):
    return db.query(models.Document).all()

@router.get("/{id}")
def read_document(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Document).filter(models.Document.id == id).first() or f"No document with {id} id has been found."

@router.post("/create_sample_documents/")
# @TODO remove this later
def create_sample_documents(db: Session = Depends(get_session_local), amount: int = 10):
    documents = [generate_fake_document(db) for _ in range(amount)]
    db.add_all(documents)
    db.commit()
    return {"message": "Sample documents created"}
