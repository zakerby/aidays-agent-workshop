# Description: Dockerfile for the app service which is a Python Flask application

# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install stress-ng
RUN apt-get update && apt-get install -y stress-ng && rm -rf /var/lib/apt/lists/*


# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Specify the command to run on container start
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]