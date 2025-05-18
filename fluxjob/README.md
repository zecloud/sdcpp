# fluxjob

## Purpose

The `fluxjob` folder contains the code for processing tasks related to flux. This includes downloading models, generating images, and managing Azure Blob Storage and Queue Storage.

## Instructions to Run the Code

1. Build the Docker image:
   ```bash
   docker build -t fluxjob .
   ```

2. Run the Docker container:
   ```bash
   docker run fluxjob
   ```

## Contents

- `blockprocessor.py`: Manages Azure Blob Storage operations.
- `Dockerfile`: Dockerfile to build the image for fluxjob.
- `job.py`: Main script for processing flux tasks.
- `msgprocessor.py`: Manages message visibility in Azure Queue Storage.
- `queueprocessor.py`: Manages Azure Queue Storage operations.
- `requirements.txt`: Lists the Python dependencies required for fluxjob.
