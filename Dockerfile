# Use the official Python 3.9 alpine image as the base image
FROM python:3.9-slim

LABEL author="Aidan Inceer"

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app
RUN apt-get update && apt-get install -y libpq-dev build-essential wine
RUN pip install --no-cache-dir -r requirements.txt

COPY lib /app

COPY src /app/src

COPY tests /app/tests

# Copy the all files into the container
COPY main.py /app

# Run the main.py file when the container starts
CMD ["python", "main.py"]