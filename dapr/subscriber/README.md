# Dapr Subscriber

## Purpose

The `dapr/subscriber` folder contains the code for the Dapr subscriber service. This service is responsible for subscribing to messages from a Dapr pub/sub component and processing them accordingly.

## Instructions to Run the Code

1. **Build the Docker Image:**
   ```bash
   docker build -t dapr-subscriber .
   ```

2. **Run the Docker Container:**
   ```bash
   docker run dapr-subscriber
   ```

## Contents

- `app.py`: The main file for the Dapr subscriber service.
- `Dockerfile`: The Dockerfile to build the Docker image for the service.
- `infraaca.sh`: Script to deploy the service on Azure Container Apps.
- `requirements.txt`: List of Python dependencies required for the service.
- `pubsub.yaml`: Configuration file for the Dapr pub/sub component.
- `statestore.yaml`: Configuration file for the Dapr state store component.
