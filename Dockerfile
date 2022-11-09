FROM python:3.11

COPY . /app
WORKDIR /app

RUN apt update -y && apt install python3 python3-dev -y

RUN pip install -r requirements.txt