import socket
import json
import argparse
import pika
import os
from datetime import datetime
import re
from database.database import get_session_local
from database.models import DataEntry, Measurement, Detector, Experiment
from sqlalchemy import func, desc
import logging

# uncomment to debug
# logging.basicConfig(level=logging.DEBUG)


def extract_acquisition_date(filename: str) -> datetime:
    basename = os.path.basename(filename)
    pattern = r"^(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})"
    match = re.match(pattern, basename)

    if match:
        year, month, day, hour, minute = match.groups()
        try:
            result = datetime(int(year), int(month), int(day), int(hour), int(minute))
            return result
        except ValueError as e:
            return None
    else:
        return None


def receive_data(producer_ip: str, producer_port: str) -> dict:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((producer_ip, producer_port))
        print(f"Connected to producer at {producer_ip}:{producer_port}")
        buffer = ""
        client_socket.settimeout(15)
        while True:
            data = client_socket.recv(4096).decode("utf-8")
            if not data:
                break
            buffer += data
        json_data = json.loads(buffer)
        # print("Received JSON data:", json.dumps(json_data, indent=2))
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
    print("Waiting for messages...")
    channel.start_consuming()


def save_data_to_db(json_data, agent_code):
    gen = get_session_local()
    session = next(gen)
    filename = json_data["file"]
    histograms = json_data["histogram"]
    histo_dir = histograms[0]["histo_dir"] if histograms else "unknown"

    acquisition_date = extract_acquisition_date(filename)

    if acquisition_date is None:
        acquisition_date = datetime.now()

    print(session)
    detector = session.query(Detector).filter(Detector.agent_code == agent_code).first()
    if not detector:
        print(f"No detector found for agent_code: {agent_code}")
        return

    experiment = (
        session.query(Experiment).filter(Experiment.detector_id == detector.id).first()
    )
    if not experiment:
        print(f"No experiment found for detector_id: {detector.id}")
        return

    measurement_match = session.query(Measurement).filter(
        Measurement.experiment_id == experiment.id
    )
    measurement = measurement_match.order_by(desc(Measurement.created_at)).first()
    if not measurement:
        print(f"No measurement found for experiment_id: {experiment.id}")
        return
    print(
        f"agent_code: {agent_code}, detector: {detector.id}, experiment: {experiment.id}, measurement: {measurement}"
    )

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
        print(f"Failed to insert data entry: {e}")
    finally:
        session.close()


def callback(ch, method, properties, body):
    producer_info = json.loads(body.decode())
    address, port = producer_info["ip"], producer_info["port"]
    agent_code = producer_info["agent_code"]
    print(f"Received producer IP and port info: {producer_info}")
    try:
        json_data = receive_data(address, port)
    except ConnectionRefusedError:
        print(f"Connection to producer at {address}:{port} refused")
    except socket.timeout:
        print("No data received within 15 seconds. Exiting.")
    else:
        save_data_to_db(json_data, agent_code)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    print("DONE!")


if __name__ == "__main__":
    consume_messages()
