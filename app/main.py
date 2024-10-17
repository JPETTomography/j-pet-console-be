from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, database
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from utills.utills import generate_fake_user
from sqladmin import Admin
from admin import UserAdmin

producer = KafkaProducer(bootstrap_servers='kafka:9092')

def send_message(topic, message):
    producer.send(topic, message.encode('utf-8'))
    producer.flush()

app = FastAPI()
admin = Admin(app, database.engine)

admin.add_view(UserAdmin)

models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}

def get_session_local():
    yield database.SessionLocal()

@app.get("/users/")
def read_users(db: Session = Depends(get_session_local)):
    users = db.query(models.User).all()
    return users

@app.post("/create_sample_users/")
# @TODO remove this later
def create_sample_users(db: Session = Depends(get_session_local), amount: int = 0):
    users = [generate_fake_user() for _ in range(amount)]
    db.add_all(users)
    db.commit()
    return {"message": "Sample users created"}


@app.post("/send_worker/")
def send_message_worker(message: str):
    send_message('worker_topic', message)
    return {"message": "Message sent"}

@app.post("/send_agent/")
def send_message_agent(message: str):
    send_message('agent_topic', message)
    return {"message": "Message sent"}
