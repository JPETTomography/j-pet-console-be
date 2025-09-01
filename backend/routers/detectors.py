import random

import faker
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import database.models as models
from backend.auth import Role, get_current_user, get_current_user_with_role
from backend.routers.common import generate_models
from database.database import get_session_local

router = APIRouter(dependencies=[Depends(get_current_user)])


class DetectorBase(BaseModel):
    name: str = Field(..., example="Detector Name")
    description: str = Field(
        ..., example="A detailed description of the detector"
    )
    status: str = Field(..., example="online")
    agent_code: str = Field(
        ..., example="550e8400-e29b-41d4-a716-446655440000"
    )


@router.get("/")
def read_detectors(db: Session = Depends(get_session_local)):
    return db.query(models.Detector).all()


@router.get("/{id}")
def read_detector(id: str, db: Session = Depends(get_session_local)):
    detector = (
        db.query(models.Detector).filter(models.Detector.id == id).first()
    )
    if not detector:
        raise HTTPException(
            status_code=404, detail=f"No detector with id {id} found."
        )
    return detector


@router.post("/new")
def create_detector(
    detector_data: DetectorBase,
    db: Session = Depends(get_session_local),
    current_user=Depends(get_current_user_with_role(Role.COORDINATOR)),
):
    try:
        detector = models.Detector(
            name=detector_data.name,
            description=detector_data.description,
            status=detector_data.status,
            agent_code=detector_data.agent_code,
        )
        db.add(detector)
        db.commit()
        db.refresh(detector)
        return {
            "message": "Detector successfully created",
            "detector": detector,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create detector: {str(e)}"
        )


@router.patch("/{id}/edit")
def edit_detector(
    id: str,
    detector_data: DetectorBase,
    db: Session = Depends(get_session_local),
    current_user=Depends(get_current_user_with_role(Role.COORDINATOR)),
):
    try:
        detector = (
            db.query(models.Detector).filter(models.Detector.id == id).first()
        )
        if not detector:
            raise HTTPException(status_code=404, detail="Detector not found")

        detector.name = detector_data.name
        detector.description = detector_data.description
        detector.status = detector_data.status
        detector.agent_code = detector_data.agent_code

        db.commit()
        db.refresh(detector)
        return {"message": "Detector updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update detector: {str(e)}"
        )


generator = faker.Faker()


def generate_fake_detector(db: Session = None):
    i = 0
    while True:
        ending = i % 10
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            status=random.choice(
                [
                    "online",
                    "offline",
                    "damaged",
                    "in-repair",
                    "commissioned",
                    "decommissioned",
                ]
            ),
            agent_code=f"550e8400-e29b-41d4-a716-44665544000{ending}",
        )
        i += 1


@router.post("/create_sample_detectors/")
def create_sample_detectors(
    db: Session = Depends(get_session_local), amount: int = 10, fake_data=None
):
    detectors = generate_models(
        models.Detector, generate_fake_detector, db, amount, fake_data
    )
    try:
        db.add_all(detectors)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create detectors"
        )
    return {"message": "Sample detectors created"}
