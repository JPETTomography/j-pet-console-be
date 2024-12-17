from datetime import timedelta
import faker
from database.models import User, Detector, Experiment, Tag, Radioisotope, Measurement, DataEntry, MeteoReadout
import random
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

generator = faker.Faker()

def get_random_user(db: Session):
    return db.query(User).order_by(func.random()).first()

def generate_fake_user():
    return User(
        name=generator.name(),
        email=generator.unique.email(),
        password="Tajne123",
        role=random.choices([None, "shifter", "coordinator", "admin"], weights=(50, 25, 15, 10))[0],
    )

def generate_user(name, email, password, role):
    return User(
        name=name,
        email=email,
        password=password,
        role=role,
    )

def get_random_detector(db: Session):
    return db.query(Detector).order_by(func.random()).first()

def generate_fake_detector():
    return Detector(
        name=generator.catch_phrase(),
        description=generator.text(max_nb_chars=200),
        status=random.choice(["online", "offline", "damaged", "in-repair", "commissioned", "decommissioned"]),
        agent_code=uuid.uuid4().hex
    )

def get_random_experiment(db: Session):
    return db.query(Experiment).order_by(func.random()).first()

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
        coordinator_id=get_random_user(db).id,
        detector_id=get_random_detector(db).id
    )

def get_random_tag(db: Session):
    return db.query(Tag).order_by(func.random()).first()

def get_random_tags(db: Session, amount = 1):
    return db.query(Tag).order_by(func.random()).limit(amount).all()

def generate_fake_tag():
    color = "%06x" % random.randint(0, 0xFFFFFF)
    return Tag(
        name=generator.catch_phrase().partition(" ")[0],
        description=generator.text(max_nb_chars=200),
        color=color
    )

def get_random_radioisotope(db: Session):
    return db.query(Radioisotope).order_by(func.random()).first()

def get_random_radioisotopes(db: Session, amount = 1):
    return db.query(Radioisotope).order_by(func.random()).limit(amount).all()

def generate_fake_radioisotope():
    return Radioisotope(
        name=generator.catch_phrase(),
        description=generator.text(max_nb_chars=200),
        activity=float(random.random()),
        halftime=float(random.random())
    )

def get_random_measurement(db: Session):
    return db.query(Measurement).order_by(func.random()).first()

def generate_fake_measurement(db: Session):
    return Measurement(
        name=generator.catch_phrase(),
        description=generator.text(max_nb_chars=200),
        directory="/".join([generator.catch_phrase().partition(" ")[0] for _ in range(2)]),
        number_of_files=random.randint(1, 10),
        patient_reference=generator.text(max_nb_chars=200),
        shifter_id=get_random_user(db).id,
        experiment_id=get_random_experiment(db).id,
        tags=get_random_tags(db, random.randint(0, 2)),
        radioisotopes=get_random_radioisotopes(db, random.randint(0, 2))
    )

def get_random_data_entry(db: Session):
    return db.query(DataEntry).order_by(func.random()).first()

def generate_fake_data_entry(db: Session):
    return DataEntry(
        name=generator.catch_phrase(),
        histo_type=random.choice(["TH2D", "TH1D"]),
        histo_dir="/".join([generator.catch_phrase().partition(" ")[0] for _ in range(2)]),
        # daq_time=generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
        # agent_time=generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
        # reco_finish=generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
        # observable_evt_num=random.randint(0, 100),
        # is_correct=random.choices([True, False], weights=(95, 5))[0],
        measurement_id=get_random_measurement(db).id
    )

def generate_fake_meteo_readout(db: Session):
    return MeteoReadout(
        station_time=generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
        agent_time=generator.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
        p_atm=float(random.random()),
        p_1=float(random.random()),
        p_2=float(random.random()),
        hum_1=float(random.random()),
        hum_2=float(random.random()),
        temp_1=float(random.random()),
        temp_2=float(random.random()),
        measurement_id=get_random_measurement(db).id
    )
