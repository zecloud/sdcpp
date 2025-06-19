# Dapr Publisher

## Purpose

The `dapr/publisher` folder contains the code for the Dapr publisher service. This service is responsible for publishing messages to a Dapr pub/sub component.

## Instructions to Run the Code

1. **Build the Docker image:**
   ```bash
   docker build -t dapr-publisher .
   ```

2. **Run the Docker container:**
   ```bash
   docker run -p 8000:8000 dapr-publisher
   ```

3. **Deploy to Azure Container Apps:**
   - Use the `infraaca.sh` script to deploy the service to Azure Container Apps.

## Files and Their Purposes

- `app.py`: The main file for the Dapr publisher service.
- `Dockerfile`: The Dockerfile to build the Docker image for the service.
- `infraaca.sh`: Script to deploy the service to Azure Container Apps.
- `requirements.txt`: List of Python dependencies required for the service.
