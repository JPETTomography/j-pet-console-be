from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database.models as models
import database.database as database
import pika
from sqladmin import Admin
from backend.admin import UserAdmin, DetectorAdmin, ExperimentAdmin, TagAdmin, RadioisotopeAdmin, MeasurementAdmin, DataEntryAdmin, MeteoReadoutAdmin
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_session_local
from backend.routers import users, detectors, experiments, tags, radioisotopes, measurements, data_entry, meteo_readouts
from backend.auth import create_access_token
from backend.fake_data.read_fake_data import fake_json
import json

rabbitmq_host = "rabbitmq"
credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters(
    rabbitmq_host,  # replace with RabbitMQ server IP if not local
    5672,         # default RabbitMQ port
    '/',
    credentials
)
 
def send_message(topic, message):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declare a queue
    channel.queue_declare(queue='task_queue', durable=True)
    
    # Publish a message
    channel.basic_publish(
        exchange='',
        routing_key='agent_topic',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        ))
    
    print(f"Sent: {message}")
    connection.close()


app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(detectors.router, prefix="/detectors", tags=["detectors"])
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(radioisotopes.router, prefix="/radioisotopes", tags=["radioisotopes"])
app.include_router(measurements.router, prefix="/measurements", tags=["measurements"])
app.include_router(data_entry.router, prefix="/data_entry", tags=["data_entry"])
app.include_router(meteo_readouts.router, prefix="/meteo_readouts", tags=["meteo_readouts"])

origins = [
    "http://localhost:3000", # local development
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = Admin(app, database.engine)
admin.add_view(UserAdmin)
admin.add_view(DetectorAdmin)
admin.add_view(ExperimentAdmin)
admin.add_view(TagAdmin)
admin.add_view(RadioisotopeAdmin)
admin.add_view(MeasurementAdmin)
admin.add_view(DataEntryAdmin)
admin.add_view(MeteoReadoutAdmin)

models.Base.metadata.create_all(bind=database.engine)


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session_local)):
    user = db.query(models.User).filter(
        models.User.email == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/seed_random")
def seed_random(db: Session = Depends(get_session_local), amount: int = 10):
    users.create_test_users(db)
    detectors.create_sample_detectors(db, amount)
    experiments.create_sample_experiments(db, amount)
    tags.create_sample_tags(db, amount)
    radioisotopes.create_sample_radioisotopes(db, amount)
    measurements.create_sample_measurements(db, amount)
    data_entry.create_sample_data_entries(db, amount)
    meteo_readouts.create_sample_meteo_readouts(db, amount)
    return {"message": "Successfully seeded DB"}

@app.get("/seed")
def seed(db: Session = Depends(get_session_local), amount: int = 10):
    fake_data = fake_json("backend/fake_data/Believable fake J-PET database - Sheet1.tsv")
    users.create_test_users(db)
    detectors.create_sample_detectors(db, fake_data=fake_data['Detector'])
    experiments.create_sample_experiments(db, fake_data=fake_data['Experiment'])
    tags.create_sample_tags(db, fake_data=fake_data['Tag'])
    radioisotopes.create_sample_radioisotopes(db, fake_data=fake_data['Radioisotope'])
    measurements.create_sample_measurements(db, fake_data=fake_data['Measurement'])
    data_entry.create_sample_data_entries(db, amount)
    meteo_readouts.create_sample_meteo_readouts(db, amount)
    return {"message": "Successfully seeded DB"}


@app.post("/send_worker/")
def send_message_worker(message: str):
    send_message('worker_topic', message)
    return {"message": "Message sent"}


@app.post("/send_agent/")
def send_message_agent(message: str):
    send_message('agent_topic', json.dumps({"task": "add_random_test_data"}))
    return {"message": "Message sent"}
