from fastapi import APIRouter, Depends, HTTPException, Form, Query
from typing import Optional
from sqlalchemy.orm import Session
from backend.auth import get_current_user
import database.models as models
from backend.auth import verify_access_token
from database.database import get_session_local
import faker
import random

router = APIRouter(dependencies=[Depends(get_current_user)])


generator = faker.Faker()

PERMITTED_ROLE = "admin"

def generate_fake_user(db: Session=None):
    while True:
        yield models.User(
            name=generator.name(),
            email=generator.unique.email(),
            password="Tajne123",
            role=random.choices([None, "shifter", "coordinator", "admin"], weights=(50, 25, 15, 10))[0],
        )

def generate_user(name: str, email: str, password: str, role: str):
    return models.User(
        name=name,
        email=email,
        password=password,
        role=role,
    )

@router.get("/")
def read_users(role: Optional[str] = Query(None, title="User Role"), db: Session = Depends(get_session_local)):
    query = db.query(models.User)
    if role is not None:
        query = query.filter(models.User.role == role)
    return query.all()

@router.post("/new")
def new_user(name: str = Form(...), email: str = Form(...), password: str = Form(...), role: str = Form(...),
             token: str = Form(...), db: Session = Depends(get_session_local)):
    user = generate_user(name=name, email=email, password=password, role=role)
    try:
        verify_access_token(token, PERMITTED_ROLE)

        db.add(user)
        db.commit()
        return {"message": "User successfully created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.get("/{id}")
def read_user(id: str, db: Session = Depends(get_session_local)):
    return db.query(models.User).filter(models.User.id == id).first() or f"No user with id: {id} found."

@router.patch("/{id}/edit")
def edit_user(id: str, name: str = Form(...), email: str = Form(...), role: str = Form(...),
              token: str = Form(...), db: Session = Depends(get_session_local)):
    try:
        verify_access_token(token, PERMITTED_ROLE)

        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.name = name
        user.email = email
        user.role = role

        db.commit()
        db.refresh(user)
        return {"message": "User successfully updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

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
