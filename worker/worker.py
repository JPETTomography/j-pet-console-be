import socket
import json
import argparse
from kafka import KafkaConsumer


TOPIC = "root_json"
def start_consumer():

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='worker-group'
    )

    producer_info = None
    for message in consumer:
        producer_info = json.loads(message.value.decode('utf-8'))
        print(f"Received producer IP and port info: {producer_info}")
        break  # Exit after receiving the first message

    consumer.close()
    print("next")

    # Extract IP and port from the received message
    producer_ip = producer_info['ip']
    producer_port = producer_info['port']

    # Connect to the producer’s socket server to receive JSON data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((producer_ip, producer_port))
        print(f"Connected to producer at {producer_ip}:{producer_port}")

        # Receive JSON data
        data = client_socket.recv(4096)
        json_data = json.loads(data.decode('utf-8'))
        print("Received JSON data:", json.dumps(json_data, indent=2))


if __name__ == "__main__":

    start_consumer()
