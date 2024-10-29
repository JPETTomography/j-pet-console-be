# main.py
from fastapi import FastAPI
from sqladmin import Admin
import models, database
from admin import UserAdmin, ExperimentAdmin
from routers import users, experiments
from kafka import KafkaProducer
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import User
from database import get_session_local
from auth import create_access_token


producer = KafkaProducer(bootstrap_servers='kafka:9092')
app = FastAPI()
admin = Admin(app, database.engine)

admin.add_view(UserAdmin)
admin.add_view(ExperimentAdmin)

models.Base.metadata.create_all(bind=database.engine)

# Include the routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session_local)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
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
    send_message('agent_topic', message)
    return {"message": "Message sent"}

def send_message(topic, message):
    producer.send(topic, message.encode('utf-8'))
    producer.flush()