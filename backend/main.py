from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
import database.database as database
import pika
from sqladmin import Admin
from backend.admin import UserAdmin, DataAdmin, ExperimentAdmin
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_session_local
from backend.routers import users, experiments
from backend.auth import create_access_token
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
app.include_router(experiments.router,
                   prefix="/experiments", tags=["experiments"])

admin = Admin(app, database.engine)
admin.add_view(UserAdmin)
admin.add_view(DataAdmin)
admin.add_view(ExperimentAdmin)

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
