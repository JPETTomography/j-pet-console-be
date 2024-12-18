from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.utills.utills import generate_fake_data_entry

router = APIRouter()

@router.get("/")
def read_data_entries(db: Session = Depends(get_session_local)):
    return db.query(models.DataEntry).all()

@router.get("/{id}")
def read_data_entrie(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.DataEntry).filter(models.DataEntry.id == id).first() or f"No data entry with {id} id has been found."

@router.post("/create_sample_data_entries/")
# @TODO remove this later
def create_sample_data_entries(db: Session = Depends(get_session_local), amount: int = 10):
    data_entry = [generate_fake_data_entry(db) for _ in range(amount)]
    try:
        db.add_all(data_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create data_entry")
    return {"message": "Sample data_entry created"}
