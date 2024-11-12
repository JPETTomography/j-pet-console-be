import time
import requests
from kafka import KafkaProducer
import socket
import json
import os

FILE_PATH = 'examplary_data/2024_02_14_14_57_dabc_24043183007.root'

HOSTNAME = 'localhost'
PORT = 12345
TOPIC = "root_json"
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
)

if __name__ == "__main__":
    # Send the IP and port information as a message to Kafka
    connection_info = {"ip": HOSTNAME, "port": PORT}
    encoded_info = json.dumps(connection_info).encode('utf-8')

    print("Starting socket server...")
    # Start a socket server to send JSON data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        print("Starting socket server...")
        server_socket.bind((HOSTNAME, PORT))
        server_socket.listen(1)
        print(f"Socket server listening on {HOSTNAME}:{PORT}...")

        producer.send(TOPIC, encoded_info)
        print(f"Sent IP and port {connection_info} to Kafka topic {TOPIC}")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}, sending JSON data...")

            encoded_data = json.dumps({"example":"test"}).encode('utf-8')
            conn.sendall(encoded_data)
            print("JSON data sent successfully.")

    print(f"Sent IP address {HOSTNAME} to Kafka topic {TOPIC}")

