import socket
import json
import argparse
import pika
from database.database import get_session_local
from database.models import DataEntry, Measurement, Detector, Experiment
from sqlalchemy import func, desc
import logging

# uncomment to debug
# logging.basicConfig(level=logging.DEBUG)


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
    session = next(get_session_local())
    title = json_data["file"]
    data = json_data["histogram"][0]
    detector = session.query(Detector).filter(Detector.agent_code == agent_code).first()
    experiment = (
        session.query(Experiment).filter(Experiment.detector_id == detector.id).first()
    )
    measurement_match = session.query(Measurement).filter(
        Measurement.experiment_id == experiment.id
    )
    measurement = measurement_match.order_by(desc(Measurement.created_at)).first()
    print(
        f"agent_code: {agent_code}, detector: {detector.id}, experiment: {experiment.id}, measurement: {measurement}"
    )

    try:
        # @TODO cover the agent_code field
        new_data_entry = DataEntry(
            data=data,
            name="unnamed_entry",
            histo_type=data["histo_type"],
            histo_dir=data["histo_dir"],
            measurement_id=measurement.id,
        )
        session.add(new_data_entry)
        session.commit()
        print(f"Inserted data entry with title '{title}'")
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
