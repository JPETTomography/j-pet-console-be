import time
from kafka import KafkaConsumer
import requests

consumer = KafkaConsumer(
    'agent_topic',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='agent-group'
)

for message in consumer:
    with open("dump.log", "w") as f:
        f.write(f"Received message: {message.value.decode('utf-8')}")
