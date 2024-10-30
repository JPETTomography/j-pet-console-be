from datetime import timedelta
import faker
from database.models import User,Experiment
import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import User

generator = faker.Faker()
def get_random_user(db: Session):
    return db.query(User).order_by(func.random()).first()

def generate_fake_user():
    return User(name=generator.name(), email =generator.unique.email(), password = "Tajne123")

def generate_fake_experiment(db: Session):
        start_date = generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None)
        end_date = start_date + timedelta(days=random.randint(1, 30))

        return Experiment(
            name=generator.catch_phrase(),
            description=generator.text(max_nb_chars=200),
            status=random.choice(["active", "completed", "pending", "failed"]),
            start_date=start_date,
            end_date=end_date,
            owner_id= get_random_user(db).id
        )