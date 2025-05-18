from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import database.models as models
from backend.auth import get_current_user
from database.database import get_session_local
from backend.routers.common import generate_models
import faker
import random

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])
ROLE = "shifter"


class RadioisotopeBase(BaseModel):
    name: str = Field(..., example="Radioisotope Name")
    description: str = Field(..., example="A detailed description of the radioisotope")
    activity: float = Field(..., example=1.23)
    halflife: float = Field(..., example=4.56)


def generate_fake_radioisotope(db: Session = None):
    while True:
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            activity=float(random.random()),
            halflife=float(random.random()),
        )


def generate_radioisotope(
    name: str, description: str, activity: float, halflife: float
):
    return models.Radioisotope(
        name=name,
        description=description,
        activity=activity,
        halflife=halflife,
    )


@router.get("/")
def read_radioisotopes(db: Session = Depends(get_session_local)):
    return db.query(models.Radioisotope).all()


@router.post("/new")
def new_radioisotope(
    radioisotope_data: RadioisotopeBase, db: Session = Depends(get_session_local)
):
    try:
        radioisotope = generate_radioisotope(
            name=radioisotope_data.name,
            description=radioisotope_data.description,
            activity=radioisotope_data.activity,
            halflife=radioisotope_data.halflife,
        )
        db.add(radioisotope)
        db.commit()
        return {"message": "Radioisotope successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create radioisotope: {str(e)}"
        )


@router.get("/{id}")
def read_radioisotope(id: str, db: Session = Depends(get_session_local)):
    radioisotope = (
        db.query(models.Radioisotope).filter(models.Radioisotope.id == id).first()
    )
    if not radioisotope:
        raise HTTPException(
            status_code=404, detail=f"No radioisotope with id: {id} found."
        )
    return radioisotope


@router.patch("/{id}/edit")
def edit_radioisotope(
    id: str,
    radioisotope_data: RadioisotopeBase,
    db: Session = Depends(get_session_local),
):
    try:
        radioisotope = (
            db.query(models.Radioisotope).filter(models.Radioisotope.id == id).first()
        )
        if not radioisotope:
            raise HTTPException(status_code=404, detail="Radioisotope not found")

        # Update fields
        radioisotope.name = radioisotope_data.name
        radioisotope.description = radioisotope_data.description
        radioisotope.activity = radioisotope_data.activity
        radioisotope.halflife = radioisotope_data.halflife

        db.commit()
        db.refresh(radioisotope)
        return {"message": "Radioisotope updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update radioisotope: {str(e)}"
        )


@router.post("/create_sample_radioisotopes/")
# @TODO remove this later
def create_sample_radioisotopes(
    db: Session = Depends(get_session_local), amount: int = 10, fake_data: dict = None
):
    radioisotopes = generate_models(
        models.Radioisotope, generate_fake_radioisotope, db, amount, fake_data
    )
    try:
        db.add_all(radioisotopes)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create radioisotopes")
    return {"message": "Sample radioisotopes created"}
