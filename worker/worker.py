import argparse
import json
import os
import re
import socket
from datetime import datetime

import pika
from loguru import logger
from sqlalchemy import desc, func

from database.database import get_session_local
from database.models import (
    DataEntry,
    Detector,
    Experiment,
    Measurement,
    MeasurementDirectory,
)


def extract_acquisition_date(filename: str) -> datetime:
    basename = os.path.basename(filename)
    pattern = r"^(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})"
    match = re.match(pattern, basename)

    if match:
        year, month, day, hour, minute = match.groups()
        try:
            result = datetime(
                int(year), int(month), int(day), int(hour), int(minute)
            )
            return result
        except ValueError as e:
            return None
    else:
        return None


def receive_data(producer_ip: str, producer_port: str) -> dict:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((producer_ip, producer_port))
        logger.info(f"Connected to producer at {producer_ip}:{producer_port}")
        buffer = ""
        client_socket.settimeout(15)
        while True:
            data = client_socket.recv(4096).decode("utf-8")
            if not data:
                break
            buffer += data
        json_data = json.loads(buffer)
        # logger.info("Received JSON data:", json.dumps(json_data, indent=2))
    return json_data


TOPIC = "root_json"

rabbitmq_host = "rabbitmq"
credentials = pika.PlainCredentials("user", "password")
parameters = pika.ConnectionParameters(rabbitmq_host, 5672, "/", credentials)


def consume_messages():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="worker_topic", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="worker_topic", on_message_callback=callback)
    logger.info("Waiting for messages...")
    channel.start_consuming()


class JPETDBException(Exception):
    pass


class ExperimentNotFound(JPETDBException):
    pass


class DetectorNotFound(JPETDBException):
    pass


def get_detector(session, agent_code: str):
    detector = (
        session.query(Detector)
        .filter(Detector.agent_code == agent_code)
        .first()
    )
    if not detector:
        raise DetectorNotFound(
            f"No detector found for agent_code: {agent_code}"
        )

    return detector


def get_experiment(session, detector: Detector, agent_code: str):

    experiment = (
        session.query(Experiment)
        .filter(Experiment.detector_id == detector.id)
        .first()
    )
    if not experiment:
        raise ExperimentNotFound(
            f"No experiment found for detector_id: {detector.id}"
        )

    return experiment


def save_folder_info_to_db(
    agent_code: str, path: str, event_type: str, timestamp: str
):
    gen = get_session_local()
    session = next(gen)
    try:
        detector = get_detector(session, agent_code)
        experiment = get_experiment(session, detector, agent_code)
    except JPETDBException as e:
        logger.error(e.msg())

    try:
        # more cases as:
        # https://python-watchdog.readthedocs.io/en/stable/_modules/watchdog/events.html#FileSystemEvent
        logger.info(f"processing folder")
        match event_type:
            case "created":
                measurement_dir = (
                    session.query(MeasurementDirectory)
                    .filter(MeasurementDirectory.path == path)
                    .first()
                )

                if measurement_dir:
                    measurement_dir.available = True
                else:
                    # Create new directory
                    measurement_dir = MeasurementDirectory(
                        path=path,
                        created_at=datetime.fromisoformat(timestamp),
                        experiment_id=experiment.id,
                        available=True,
                    )
                    logger.info(f"Creating entry: {measurement_dir}")
                    session.add(measurement_dir)
                session.commit()
            case "deleted":
                measurement_dir = (
                    session.query(MeasurementDirectory)
                    .filter(MeasurementDirectory.path == path)
                    .first()
                )
                logger.info(f"Modifying entry: {measurement_dir}")
                if measurement_dir:
                    measurement_dir.available = False
                    session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to insert data entry: {e}")
    finally:
        session.close()


def save_data_entry_to_db(json_data, agent_code):
    gen = get_session_local()
    session = next(gen)
    filename = json_data["file"]
    histograms = json_data["histogram"]
    histo_dir = histograms[0]["histo_dir"] if histograms else "unknown"

    acquisition_date = extract_acquisition_date(filename)

    logger.info(session)

    if acquisition_date is None:
        acquisition_date = datetime.now()

    try:
        detector = get_detector(session, agent_code)
        experiment = get_experiment(session, detector, agent_code)
    except JPETDBException as e:
        logger.error(e.msg())

    # @TODO this will need to change based on the directory which
    # the event comes from
    measurement_match = session.query(Measurement).filter(
        Measurement.experiment_id == experiment.id
    )
    measurement = measurement_match.order_by(
        desc(Measurement.created_at)
    ).first()
    if not measurement:
        logger.error(
            f"No measurement found for experiment_id: {experiment.id}"
        )
        return
    logger.info(f"agent_code: {agent_code}, detector: {detector.id}")
    logger.info(f"experiment: {experiment.id}, measurement: {measurement}")

    try:
        new_data_entry = DataEntry(
            data=histograms,  # The entire list of histograms
            name=f"data_from_{filename}",
            histo_dir=histo_dir,  # Directory from first histogram
            acquisition_date=acquisition_date,  # Extracted date from filename
            measurement_id=measurement.id,
        )
        session.add(new_data_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to insert data entry: {e}")
    finally:
        session.close()


def callback(ch, method, properties, body):
    json_payload = json.loads(body.decode())
    agent_code = json_payload["agent_code"]
    logger.info(f"Received message {json_payload}")
    match json_payload["message_type"]:
        case "connection_info":
            connection_data = json_payload["data"]
            address, port = connection_data["ip"], connection_data["port"]
            agent_code = connection_data["agent_code"]
            logger.info(
                f"Received producer IP and port info: {connection_data}"
            )
            try:
                json_data = receive_data(address, port)
            except ConnectionRefusedError:
                logger.error(
                    f"Connection to producer at {address}:{port} refused"
                )
            except socket.timeout:
                logger.error("No data received within 15 seconds. Exiting.")
            else:
                save_data_entry_to_db(json_data, agent_code)
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("DONE!")
        case "folder_info":
            event_data = json_payload["data"]
            save_folder_info_to_db(agent_code=agent_code, **event_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    consume_messages()
