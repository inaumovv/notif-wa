FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /usr/src/notifications_whatsapp

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /usr/src/notifications_whatsapp/
WORKDIR /usr/src/notifications_whatsapp/src/

CMD celery -A tasks.celery_app:celery_app worker -E -l info

