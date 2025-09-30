FROM python:3.11-slim

WORKDIR /app/

RUN apt-get update && apt install -y netcat-openbsd && rm -rf /var/likb/apt/lists/*
# pdbpp is a debugger for python

ADD . /app
RUN pip install -r ./backend/requirements.txt
CMD ["./common/wait-for-rabbit.sh","./backend/entrypoint.sh"]
