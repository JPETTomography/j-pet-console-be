import random

import faker
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import database.models as models
from backend.auth import get_current_user
from backend.routers.common import generate_models
from backend.utills.utills import get_random_measurement
from database.database import get_session_local

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])


def generate_fake_data_entry(db: Session = None):
    while True:
        yield dict(
            name=generator.catch_phrase(),
            histo_dir="/".join(
                [generator.catch_phrase().partition(" ")[0] for _ in range(2)]
            ),
            acquisition_date=generator.date_time_this_year(
                before_now=True, after_now=False, tzinfo=None
            ),
            measurement_id=get_random_measurement(db).id,
        )


@router.get("/")
def read_data_entries(db: Session = Depends(get_session_local)):
    return db.query(models.DataEntry).all()


@router.get("/{id}")
def read_data_entrie(id: str, db: Session = Depends(get_session_local)):
    return (
        db.query(models.DataEntry).filter(models.DataEntry.id == id).first()
        or f"No data entry with {id} id has been found."
    )


@router.post("/create_sample_data_entries/")
# @TODO remove this later
def create_sample_data_entries(
    db: Session = Depends(get_session_local),
    amount: int = 10,
    fake_data: dict = None,
):
    data_entry = generate_models(
        models.DataEntry, generate_fake_data_entry, db, amount, fake_data
    )
    try:
        db.add_all(data_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create data_entry"
        )
    return {"message": "Sample data_entry created"}
