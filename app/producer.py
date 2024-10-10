from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

producer = KafkaProducer(bootstrap_servers='kafka:9092')

def send_message(topic, message):
    producer.send(topic, message.encode('utf-8'))
    producer.flush()
