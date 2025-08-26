FROM python:3.11-slim


RUN apt-get update && apt install -y netcat-openbsd && rm -rf /var/likb/apt/lists/*
# pdbpp is a debugger for python
RUN pip install fastapi uvicorn psycopg2-binary sqlalchemy pika faker sqladmin PyJWT passlib pdbpp loguru==0.7.3

ADD . /app
WORKDIR /app/
CMD ["./common/wait-for-rabbit.sh", "./worker/entrypoint.sh"]
