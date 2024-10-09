from kafka import KafkaConsumer
import requests

consumer = KafkaConsumer(
    'my_topic',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    api_version=(3,8,0),
    group_id='worker-group'
)

# consumer = get_consumer()
# no_consumer = True
# trials = 0
# max_trials = 4
# consumer = None
# while no_consumer:
#     print("looping")
#     try:
#         consumer = get_consumer()
#         print("Consumer found")
#         no_consumer = False
#         break
#     except NoBrokersAvailable:
#         trials += 1
#         print("Waiting for consumer")
#         time.sleep(15)
#     if trials >= max_trials:
#         print("Trials exceeded")
#         raise NoBrokersAvailable()
#         break
print("Whatever")
for message in consumer:
    print(f"Received message: {message.value.decode('utf-8')}")
