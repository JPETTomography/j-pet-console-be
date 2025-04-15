from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from backend.auth import get_current_user
from backend.routers.common import generate_models
import faker
import random

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])

def generate_fake_tag(db: Session=None):
    while True:
        color = "%06x" % random.randint(0, 0xFFFFFF)
        yield dict(
            name=generator.catch_phrase().partition(" ")[0],
            description=generator.text(max_nb_chars=200),
            color=color
        )


@router.get("/")
def read_tags(db: Session = Depends(get_session_local)):
    return db.query(models.Tag).all()

@router.get("/{id}")
def read_tag(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Tag).filter(models.Tag.id == id).first() or f"No tag with {id} id has been found."

@router.post("/create_sample_tags/")
# @TODO remove this later
def create_sample_tags(db: Session = Depends(get_session_local), amount: int = 10, fake_data:dict=None):
    tags = generate_models(models.Tag, generate_fake_tag, db, amount, fake_data)
    try:
        db.add_all(tags)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create tags")
    return {"message": "Sample tags created"}
