from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import database.models as models
from backend.auth import verify_access_token
from database.database import get_session_local
from backend.routers.common import generate_models
import uuid
import faker
import random

generator = faker.Faker()
router = APIRouter()

PERMITTED_ROLE = "coordinator"

def generate_fake_detector(db: Session=None):
    i = 0
    while True:
        ending = i%10
        yield dict(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            status=random.choice(["online", "offline", "damaged", "in-repair", "commissioned", "decommissioned"]),
            # agent_code=uuid.uuid4().hex
            # @TODO this is for demo purposes
            agent_code=f"550e8400-e29b-41d4-a716-44665544000{ending}"
        )
        i+=1

def generate_detector(name: str, description: str, status: str, agent_code: str):
    return models.Detector(
        name=name,
        description=description,
        status=status,
        agent_code=agent_code
    )

@router.get("/")
def read_detectors(db: Session = Depends(get_session_local)):
    return db.query(models.Detector).all()

@router.post("/new")
def new_detector(name: str = Form(...), description: str = Form(...), status: str = Form(...), agent_code: str = Form(...),
                 token: str = Form(...), db: Session = Depends(get_session_local)):
    detector = generate_detector(name=name, description=description, status=status, agent_code=agent_code)
    try:
        verify_access_token(token, PERMITTED_ROLE, db)

        db.add(detector)
        db.commit()
        return {"message": "Detector successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create detector: {str(e)}")

@router.get("/{id}")
def read_detector(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.Detector).filter(models.Detector.id == id).first() or f"No detector with {id} id has been found."

@router.patch("/{id}/edit")
def edit_detector(id: str, name: str = Form(...), description: str = Form(...), status: str = Form(...), agent_code: str = Form(...),
                  token: str = Form(...), db: Session = Depends(get_session_local)):
    try:
        verify_access_token(token, PERMITTED_ROLE, db)

        detector = db.query(models.Detector).filter(models.Detector.id == id).first()
        if not detector:
            raise HTTPException(status_code=404, detail="Detector not found")

        detector.name = name
        detector.description = description
        detector.status = status
        detector.agent_code = agent_code

        db.commit()
        db.refresh(detector)
        return {"message": "Detector updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update detector: {str(e)}")

@router.post("/create_sample_detectors/")
# @TODO remove this later
def create_sample_detectors(db: Session = Depends(get_session_local), amount: int = 10, fake_data=None):
    detectors = generate_models(models.Detector, generate_fake_detector, db, amount, fake_data)
    try:
        db.add_all(detectors)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create detectors")
    return {"message": "Sample detectors created"}
