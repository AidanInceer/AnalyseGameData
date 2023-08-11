# Use the official Python 3.9 alpine image as the base image
FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

# Copy the requirements.txt file into the container
COPY requirements.txt ./
RUN apt-get update && apt-get install -y libpq-dev build-essential wine
RUN pip install --no-cache-dir -r requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./


# Run the main.py file when the container starts
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app