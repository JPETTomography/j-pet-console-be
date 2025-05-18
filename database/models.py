from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    Float,
    String,
    text,
    TIMESTAMP,
    ForeignKey,
    event,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base
from sqlalchemy.dialects.postgresql import JSONB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=func.now(),
        nullable=False,
    )
    experiments = relationship("Experiment", back_populates="coordinator")
    measurements = relationship("Measurement", back_populates="shifter")

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password)

    def hash_password(self):
        self.password = pwd_context.hash(self.password)


@event.listens_for(User, "before_insert")
def hash_password_before_insert(_mapper, connection, target):
    if target.password:
        target.hash_password()


class Detector(Base):
    __tablename__ = "detectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    agent_code = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=func.now(),
        nullable=False,
    )
    experiments = relationship("Experiment", back_populates="detector")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    location = Column(String, nullable=False)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=func.now(),
        nullable=False,
    )
    coordinator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coordinator = relationship("User", back_populates="experiments")
    detector_id = Column(Integer, ForeignKey("detectors.id"), nullable=False)
    detector = relationship("Detector", back_populates="experiments")
    measurements = relationship("Measurement", back_populates="experiment")


class TagMeasurement(Base):
    __tablename__ = "tag_measurement"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    measurement_id = Column(Integer, ForeignKey("measurements.id"), nullable=False)


class RadioisotopeMeasurement(Base):
    __tablename__ = "radioisotope_measurement"

    id = Column(Integer, primary_key=True, index=True)
    radioisotope_id = Column(Integer, ForeignKey("radioisotopes.id"), nullable=False)
    measurement_id = Column(Integer, ForeignKey("measurements.id"), nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    color = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=func.now(),
        nullable=False,
    )
    measurements = relationship(
        "Measurement", secondary="tag_measurement", back_populates="tags"
    )


class Radioisotope(Base):
    __tablename__ = "radioisotopes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    activity = Column(Float, nullable=False)
    halflife = Column(Float, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=func.now(),
        nullable=False,
    )
    measurements = relationship(
        "Measurement",
        secondary="radioisotope_measurement",
        back_populates="radioisotopes",
    )


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    directory = Column(String, nullable=False)
    number_of_files = Column(Integer, nullable=False)
    patient_reference = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=func.now(),
        nullable=False,
    )
    shifter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shifter = relationship("User", back_populates="measurements")
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    experiment = relationship("Experiment", back_populates="measurements")
    tags = relationship(
        "Tag", secondary="tag_measurement", back_populates="measurements"
    )
    radioisotopes = relationship(
        "Radioisotope",
        secondary="radioisotope_measurement",
        back_populates="measurements",
    )
    data_entry = relationship("DataEntry", back_populates="measurement")
    meteo_readouts = relationship("MeteoReadout", back_populates="measurement")


class DataEntry(Base):
    __tablename__ = "data_entry"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    histo_type = Column(String, nullable=False)
    histo_dir = Column(String, nullable=False)
    # THIS WILL BE PROVIDED IN data column
    # daq_time = Column(TIMESTAMP(timezone=True), nullable=False)
    # agent_time = Column(TIMESTAMP(timezone=True), nullable=False)
    # reco_finish = Column(TIMESTAMP(timezone=True), nullable=False)
    # observable_evt_num = Column(Integer, nullable=False)
    # is_correct = Column(Boolean, default=False)
    data = Column(JSONB)
    # created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    # updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    measurement_id = Column(Integer, ForeignKey("measurements.id"), nullable=False)
    measurement = relationship("Measurement", back_populates="data_entry")


class MeteoReadout(Base):
    __tablename__ = "meteo_readouts"

    id = Column(Integer, primary_key=True, index=True)
    station_time = Column(TIMESTAMP(timezone=True), nullable=False)
    agent_time = Column(TIMESTAMP(timezone=True), nullable=False)
    p_atm = Column(Float, nullable=False)
    p_1 = Column(Float, nullable=False)
    p_2 = Column(Float, nullable=False)
    hum_1 = Column(Float, nullable=False)
    hum_2 = Column(Float, nullable=False)
    temp_1 = Column(Float, nullable=False)
    temp_2 = Column(Float, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=func.now(),
        nullable=False,
    )
    measurement_id = Column(Integer, ForeignKey("measurements.id"), nullable=False)
    measurement = relationship("Measurement", back_populates="meteo_readouts")
