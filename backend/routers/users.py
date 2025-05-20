from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.auth import get_current_user
import database.models as models
from database.database import get_session_local
import faker
import random

router = APIRouter(dependencies=[Depends(get_current_user)])


generator = faker.Faker()
def generate_fake_user(db: Session=None):
    while True:
        yield models.User(
            name=generator.name(),
            email=generator.unique.email(),
            password="Tajne123",
            role=random.choices([None, "shifter", "coordinator", "admin"], weights=(50, 25, 15, 10))[0],
        )

def generate_user(name, email, password, role):
    return models.User(
        name=name,
        email=email,
        password=password,
        role=role,
    )

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
    try:
        db.add_all(users)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create users")
    return {"message": "Sample users created"}

@router.post("/create_test_users/")
# @TODO remove this later
def create_test_users(db: Session = Depends(get_session_local)):
    users = ["user", "shifter", "coordinator", "admin"]
    generated_users = [
        generate_user(
            user,
            user + "@gmail.com",
            user,
            user if user != "user" else None
        ) for user in users
    ]
    try:
        db.add_all(generated_users)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create test users")
    return {"message": "Test users created"}
