import random

import faker
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import database.models as models
from backend.auth import Role, get_current_user, get_current_user_with_role
from backend.routers.common import generate_models
from database.database import get_session_local

generator = faker.Faker()
router = APIRouter(dependencies=[Depends(get_current_user)])


class TagBase(BaseModel):
    name: str = Field(..., example="Tag Name")
    description: str = Field(..., example="A detailed description of the tag")
    color: str = Field(..., example="FFFFFF")


def generate_fake_tag(db: Session = None):
    while True:
        color = "%06x" % random.randint(0, 0xFFFFFF)
        yield dict(
            name=generator.catch_phrase().partition(" ")[0],
            description=generator.text(max_nb_chars=200),
            color=color,
        )


def generate_tag(name: str, description: str, color: str):
    return models.Tag(
        name=name,
        description=description,
        color=color,
    )


@router.get("/")
def read_tags(db: Session = Depends(get_session_local)):
    return db.query(models.Tag).all()


@router.post("/new")
def new_tag(
    tag_data: TagBase,
    db: Session = Depends(get_session_local),
    _=Depends(get_current_user_with_role(Role.SHIFTER)),
):
    tag = generate_tag(
        name=tag_data.name,
        description=tag_data.description,
        color=tag_data.color,
    )
    try:
        db.add(tag)
        db.commit()
        return {"message": "Tag successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create tag: {str(e)}"
        )


@router.get("/{id}")
def read_tag(id: str, db: Session = Depends(get_session_local)):
    tag = db.query(models.Tag).filter(models.Tag.id == id).first()
    if not tag:
        raise HTTPException(
            status_code=404, detail=f"No tag with id {id} found."
        )
    return tag


@router.patch("/{id}/edit")
def edit_tag(
    id: str,
    tag_data: TagBase,
    db: Session = Depends(get_session_local),
    _=Depends(get_current_user_with_role(Role.SHIFTER)),
):
    try:
        tag = db.query(models.Tag).filter(models.Tag.id == id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        tag.name = tag_data.name
        tag.description = tag_data.description
        tag.color = tag_data.color

        db.commit()
        db.refresh(tag)
        return {"message": "Tag successfully updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update tag: {str(e)}"
        )


@router.post("/create_sample_tags/")
# @TODO remove this later
def create_sample_tags(
    db: Session = Depends(get_session_local),
    amount: int = 10,
    fake_data: dict = None,
):
    tags = generate_models(
        models.Tag, generate_fake_tag, db, amount, fake_data
    )
    try:
        db.add_all(tags)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create tags")
    return {"message": "Sample tags created"}
