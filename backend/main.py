from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database.models as models
import database.database as database
import pika
from sqladmin import Admin
from backend.admin import UserAdmin, DetectorAdmin, ExperimentAdmin, TagAdmin, DataAdmin
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_session_local
from backend.routers import users, detectors, experiments, tags
from backend.auth import create_access_token
import json
from pydantic import BaseModel
from database.models import Detector
import uuid

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
admin.add_view(DataAdmin)

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


@app.post("/send_worker/")
def send_message_worker(message: str):
    send_message('worker_topic', message)
    return {"message": "Message sent"}


@app.post("/send_agent/")
def send_message_agent(message: str):
    send_message('agent_topic', json.dumps({"task": "add_random_test_data"}))
    return {"message": "Message sent"}

# Pydantic Model for input validation
class DetectorCreate(BaseModel):
    name: str
    description: str
    status: str
    agent_code: str


@app.post("/detectors/", response_model=dict)
def create_detector(detector: DetectorCreate, db: Session = Depends(get_session_local)):
    agent_code = uuid.uuid4().hex
    new_detector = Detector(
        name=detector.name,
        description=detector.description,
        status=detector.status,
        agent_code=agent_code,
    )
    try:
        db.add(new_detector)
        db.commit()
        db.refresh(new_detector)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create detector")

    return {
        "id": new_detector.id,
        "name": new_detector.name,
        "description": new_detector.description,
        "status": new_detector.status,
        "agent_code": new_detector.agent_code,
    }
