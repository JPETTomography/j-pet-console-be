from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, database
import producer

app = FastAPI()

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
def create_sample_users(db: Session = Depends(get_session_local)):
    sample_users = [
        models.User(name="Alice"),
        models.User(name="Bob"),
        models.User(name="Charlie")
    ]
    db.add_all(sample_users)
    db.commit()
    return {"message": "Sample users created"}


@app.post("/send/")
def send_message(message: str):
    producer.send_message('my_topic', message)
    return {"message": "Message sent"}
