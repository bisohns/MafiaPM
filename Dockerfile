FROM python:3.6-slim
MAINTAINER Me


# Start Installing the Basic Dependencies
RUN pip install --upgrade pip
RUN pip install gunicorn

RUN mkdir -p /sanic/config
RUN mkdir -p /sanic/mafiapm

COPY config/* /sanic/config/
COPY mafiapm/ /sanic/mafiapm/
COPY requirements.txt /sanic
COPY run.py /sanic/run.py
COPY .env /sanic/.env

WORKDIR /sanic
RUN find . -type f

ENV SANIC_SERVER_PORT 8000
ENV SANIC_SERVER_HOST 0.0.0.0

EXPOSE 8022


ENTRYPOINT ["python", "run.py"]

