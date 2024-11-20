from datetime import timedelta
import faker
from database.models import User, Experiment
import random
from sqlalchemy.orm import Session
from sqlalchemy import func

generator = faker.Faker()

def get_random_user(db: Session):
    return db.query(User).order_by(func.random()).first()

def generate_fake_user():
    return User(name=generator.name(), email=generator.unique.email(), password="Tajne123")

def generate_fake_experiment(db: Session):
    start_date = generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None)
    end_date = random.choice([start_date + timedelta(days=random.randint(1, 30)), None])

    return Experiment(
        name=generator.catch_phrase(),
        description=generator.text(max_nb_chars=200),
        status=random.choice(["draft", "ongoing", "closed", "archived"]),
        location=generator.city(),
        start_date=start_date,
        end_date=end_date,
        coordinator_id=get_random_user(db).id
    )
