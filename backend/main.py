from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import database.models as models
import database.database as database
from kafka import KafkaProducer
from sqladmin import Admin
from backend.admin import UserAdmin, DataAdmin, ExperimentAdmin
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_session_local
from backend.routers import users, experiments,documents
from backend.auth import create_access_token

producer = KafkaProducer(bootstrap_servers='kafka:9092')

def send_message(topic, message):
    producer.send(topic, message.encode('utf-8'))
    producer.flush()

app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])

admin = Admin(app, database.engine)
admin.add_view(UserAdmin)
admin.add_view(DataAdmin)
admin.add_view(ExperimentAdmin)

models.Base.metadata.create_all(bind=database.engine)


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session_local)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
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
