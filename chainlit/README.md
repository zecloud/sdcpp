# Chainlit Folder

## Purpose

The `chainlit` folder contains the code for the Chainlit application. This application is responsible for generating images using Stable Diffusion and FLUX models. It provides an interface for users to input prompts and receive generated images.

## Instructions to Run the Code

1. **Build the Docker Image:**
   ```bash
   docker build -t chainlit .
   ```

2. **Run the Docker Container:**
   ```bash
   docker run -p 8000:8000 chainlit
   ```

## Files and Their Purposes

- `app.py`: The main application file for Chainlit. It contains the logic for downloading models, initializing Stable Diffusion, and handling user prompts to generate images.
- `Dockerfile`: The Dockerfile for building the Chainlit application image.
- `infraaca.sh`: A script for deploying the Chainlit application on Azure Container Apps.
- `requirements.txt`: A list of Python dependencies required for the Chainlit application.
