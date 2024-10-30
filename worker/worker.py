import sys
sys.path.append('../backend')
#@TODO solve this, sqlalchemy is in backend but we use it here
import time
from kafka import KafkaConsumer
import requests
import socket
import uuid
import ROOT
import numpy as np

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Document, Base

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

DATABASE_URI = "postgresql://user:password@postgres_db/mydatabase"
#@TODO cover the source of the adresss

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

consumer = KafkaConsumer(
    'worker_topic',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='worker-group'
)

def insert_document(title, data):
    session = Session()
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

def work_file(filename):
    file = ROOT.TFile.Open("./dabc_17334031817.tslot.calib.root")
    tree = file.Get("TimeWindowCreator subtask 0 stats")
    llt = tree.Get("LL_per_PM")
    nbins = llt.GetNbinsX()
    x = [llt.GetBinCenter(i) for i in range(1, nbins + 1)]
    y = [llt.GetBinContent(i) for i in range(1, nbins + 1)]
    title="Unstructured Data Example"
    data={
        "x": x,
        "y": y,
    }
    insert_document(title, data)


def receive_file_via_socket_tmp(sender_ip, sender_port, output_file):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((sender_ip, int(sender_port)))
            with open(output_file, 'wb') as f:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)
    except Exception as e:
        print(f"Error occurred while receiving file: {e}")

def receive_file_via_socket(sender_ip, sender_port, output_file):
    pass

if __name__ == "__main__":
    for message in consumer:
        print(message)
        print(message.value)
        print(type(message))
        print(type(message.value))
        sender_info = message.value.decode("utf-8")
        sender_ip, sender_port = sender_info.split(":")

        print(f"Received message with sender info: {sender_info}")
        filename = f"{uuid.uuid4()}.root"
        receive_file_via_socket(sender_ip, sender_port, filename)
        work_file(filename)
    consumer.close()
