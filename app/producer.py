from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import time

# producer = KafkaProducer(bootstrap_servers='kafka:9092',  api_version=(0,11,5))
producer = KafkaProducer(bootstrap_servers='kafka:9092', api_version=(3,8,0))
# no_producer = True
# trials = 0
# producer = None
# max_trials = 4
# while no_producer:
#     try:
#         producer = get_producer()
#         print("Producer found")
#         no_producer = False
#         break
#     except NoBrokersAvailable:
#         trials += 1
#         print("Waiting for producer")
#         time.sleep(15)
#     if trials >= max_trials:
#         raise NoBrokersAvailable
#         break

def send_message(topic, message):
    producer.send(topic, message.encode('utf-8'))
    producer.flush()
