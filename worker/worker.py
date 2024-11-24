import socket
import json
import argparse
import pika
from database.database import get_session_local
from database.models import Document


def receive_data(producer_ip: str, producer_port: str) -> dict:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((producer_ip, producer_port))
        print(f"Connected to producer at {producer_ip}:{producer_port}")

        buffer = ""
        # Receive JSON data
        while True:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break
            buffer += data
        json_data = json.loads(buffer)
        print("Received JSON data:", json.dumps(json_data, indent=2))

    return json_data


TOPIC = "root_json"

rabbitmq_host = "rabbitmq"
credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters(
    rabbitmq_host,  # replace with RabbitMQ server IP if not local
    5672,         # default RabbitMQ port
    '/',
    credentials
)
import logging
logging.basicConfig(level=logging.DEBUG)

def consume_messages():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the queue (make sure it exists)
    channel.queue_declare(queue='worker_topic', durable=True)
    # Set up consumer
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue='worker_topic', on_message_callback=callback)

    print("Waiting for messages...")
    channel.start_consuming()

def save_data_to_db(json_data):
    session = get_session_local()
    title = json_data['file']
    data = json_data['histogram']
    try:
        new_document = Document(title=title, data=data)
        session.add(new_document)
        session.commit()
        print(f"Inserted document with title '{title}'")
    except Exception as e:
        session.rollback()
        print(f"Failed to insert document: {e}")
    finally:
        session.close()


def callback(ch, method, properties, body):
    producer_info = json.loads(body.decode())
    address, port = producer_info['ip'], producer_info['port']
    print(f"Received producer IP and port info: {producer_info}")
    try:
        json_data = receive_data(address, port)
    except ConnectionRefusedError:
        print(f"Connection to producer at {address}:{port} refused")
    else:
        save_data_to_db(json_data)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    print("DONE!")





if __name__ == "__main__":
    consume_messages()

