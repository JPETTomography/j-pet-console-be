import os

from passlib.context import CryptContext
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    event,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base

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

    def __str__(self):
        return f"<User id={self.id} name={self.name} email={self.email}>"


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

    def __str__(self):
        return f"<Detector id={self.id} name={self.name}>"


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
    reference_data = Column(JSONB)

    def __str__(self):
        return f"<Experiment id={self.id} name={self.name}>"

    measurement_directories = relationship(
        "MasurementDirectory", back_populates="experiment"
    )


class TagMeasurement(Base):
    __tablename__ = "tag_measurement"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    measurement_id = Column(
        Integer, ForeignKey("measurements.id"), nullable=False
    )

    def __str__(self):
        return f"<TagMeasurement id={self.id} tag_id={self.tag_id} measurement_id={self.measurement_id}>"


class RadioisotopeMeasurement(Base):
    __tablename__ = "radioisotope_measurement"

    id = Column(Integer, primary_key=True, index=True)
    radioisotope_id = Column(
        Integer, ForeignKey("radioisotopes.id"), nullable=False
    )
    measurement_id = Column(
        Integer, ForeignKey("measurements.id"), nullable=False
    )

    def __str__(self):
        return f"<RadioisotopeMeasurement id={self.id} radioisotope_id={self.radioisotope_id} measurement_id={self.measurement_id}>"


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

    def __str__(self):
        return f"<Tag id={self.id} name={self.name}>"


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

    def __str__(self):
        return f"<Radioisotope id={self.id} name={self.name}>"


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
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
    experiment_id = Column(
        Integer, ForeignKey("experiments.id"), nullable=False
    )
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
    comments = relationship("Comment", back_populates="measurement")
    directory = relationship(
        "MeasurementDirectory", back_populate="measurement"
    )
    directory_id = Column(
        Integer, ForeignKey("measurement_directory.id"), nullable=False
    )

    def __str__(self):
        return f"<Measurement id={self.id} name={self.name}>"


class MeasurementDirectory(Base):
    __tablename__ = "measurement_directory"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    available = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    measurement = relationship("Measurement", back_populates="directory")
    experiment = relationship(
        "Experiment", back_populates="measurement_directories"
    )
    experiment_id = Column(
        Integer, ForeignKey("experiments.id"), nullable=False
    )


class DataEntry(Base):
    __tablename__ = "data_entry"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    histo_dir = Column(String, nullable=False)
    acquisition_date = Column(TIMESTAMP(timezone=True), nullable=True)
    data = Column(JSONB)
    measurement_id = Column(
        Integer, ForeignKey("measurements.id"), nullable=False
    )
    measurement = relationship("Measurement", back_populates="data_entry")

    def __str__(self):
        return f"<DataEntry id={self.id} name={self.name}>"


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
    measurement_id = Column(
        Integer, ForeignKey("measurements.id"), nullable=False
    )
    measurement = relationship("Measurement", back_populates="meteo_readouts")

    def __str__(self):
        return (
            f"<MeteoReadout id={self.id} measurement_id={self.measurement_id}>"
        )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    measurement_id = Column(
        Integer, ForeignKey("measurements.id"), nullable=False
    )
    measurement = relationship("Measurement", back_populates="comments")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    comment_pictures = relationship(
        "CommentPicture",
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return f"<Comment id={self.id} measurement_id={self.measurement_id} user_id={self.user_id}>"


class CommentPicture(Base):
    __tablename__ = "comment_pictures"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    comment = relationship("Comment", back_populates="comment_pictures")

    def __str__(self):
        return f"<CommentPicture id={self.id} path={self.path}>"


@event.listens_for(CommentPicture, "after_delete")
def delete_picture_file(mapper, connection, target):
    if target.path:
        file_path = target.path
        if file_path.startswith("/static/"):
            file_path = file_path.replace("/static/", "")
        abs_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(abs_path):
            os.remove(abs_path)
