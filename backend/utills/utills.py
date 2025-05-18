from datetime import timedelta
import faker
from database.models import (
    User,
    Detector,
    Experiment,
    Tag,
    Radioisotope,
    Measurement,
    DataEntry,
    MeteoReadout,
)
import random
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

generator = faker.Faker()


def get_random_user(db: Session):
    return db.query(User).order_by(func.random()).first()


def get_random_detector(db: Session):
    return db.query(Detector).order_by(func.random()).first()


def get_random_experiment(db: Session):
    return db.query(Experiment).order_by(func.random()).first()


def get_random_tag(db: Session):
    return db.query(Tag).order_by(func.random()).first()


def get_random_tags(db: Session, amount=1):
    return db.query(Tag).order_by(func.random()).limit(amount).all()


def get_random_radioisotope(db: Session):
    return db.query(Radioisotope).order_by(func.random()).first()


def get_random_radioisotopes(db: Session, amount=1):
    return db.query(Radioisotope).order_by(func.random()).limit(amount).all()


def get_random_measurement(db: Session):
    return db.query(Measurement).order_by(func.random()).first()


def get_random_data_entry(db: Session):
    return db.query(DataEntry).order_by(func.random()).first()
