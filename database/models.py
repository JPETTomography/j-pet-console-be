from sqlalchemy import Column, Integer, String, text, TIMESTAMP, ForeignKey, event
from sqlalchemy.orm import relationship
from database.database import Base
from sqlalchemy.dialects.postgresql import JSONB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable = False)
    password = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    experiments = relationship("Experiment", back_populates="owner")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "password" in kwargs:
            self.hash_password()

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password)

    def hash_password(self):
        self.password = pwd_context.hash(self.password)

@event.listens_for(User, 'before_insert')
def hash_password_before_insert(_mapper, connection, target):
    if target.password:
        target.hash_password()


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="experiments")

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    data = Column(JSONB)

class Detector(Base):
    __tablename__ = "detectors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    agent_code = Column(String, nullable=False)
