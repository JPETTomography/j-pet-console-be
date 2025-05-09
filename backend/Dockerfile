FROM python:3.11-slim

WORKDIR /app/

RUN apt-get update && apt install -y netcat-openbsd && rm -rf /var/likb/apt/lists/*
# pdbpp is a debugger for python
RUN pip install fastapi uvicorn psycopg2-binary sqlalchemy pika faker sqladmin PyJWT passlib pdbpp pydantic

ADD . /app
CMD ["./common/wait-for-rabbit.sh","./backend/entrypoint.sh"]
