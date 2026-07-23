# AWS Deployment Instructions for SafeBox Web

This document outlines the steps to deploy your containerized SafeBox Web application to AWS using **AWS App Runner**. AWS App Runner is a fully managed service that makes it easy to deploy containerized web applications and APIs at scale.

## Prerequisites
1.  **AWS Account**: You need an active AWS account.
2.  **AWS CLI**: Install and configure the AWS Command Line Interface (CLI) on your local machine. Ensure you have appropriate permissions to create ECR repositories and App Runner services.
3.  **Docker**: Docker must be installed and running on your local machine to build and push the Docker image.
4.  **SafeBox Web Project**: Ensure you have the `safebox-web` project directory with all the generated files (`Dockerfile`, `main.py`, `requirements.txt`, `static/`, `.env.example`).

## Step-by-Step Deployment Guide

### Step 1: Configure Environment Variables
1.  Navigate to your `safebox-web` project directory.
2.  Create a `.env` file by copying `.env.example`:
    ```bash
    cp .env.example .env
    ```
3.  Edit the `.env` file and replace `your_openai_api_key_here` or `your_anthropic_api_key_here` with your actual API key. You only need one of them.
    ```ini
    # .env
    OPENAI_API_KEY=sk-your_openai_api_key
    # ANTHROPIC_API_KEY=sk-your_anthropic_api_key
    ```

### Step 2: Build and Tag the Docker Image
1.  Open your terminal and navigate to the `safebox-web` directory.
2.  Build your Docker image:
    ```bash
    docker build -t safebox-web .
    ```

### Step 3: Create an Amazon ECR Repository
1.  Log in to the AWS Management Console and navigate to **ECR (Elastic Container Registry)**.
2.  Click **"Create repository"**.
3.  Choose **"Private"** for visibility settings.
4.  Enter `safebox-web` as the **Repository name**.
5.  Click **"Create repository"**.

### Step 4: Authenticate Docker to Amazon ECR
1.  In the ECR console, click on the `safebox-web` repository you just created.
2.  Click **"View push commands"**.
3.  Copy the AWS CLI command for authentication (e.g., `aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<your-region>.amazonaws.com`).
4.  Paste and run this command in your terminal.

### Step 5: Tag and Push Docker Image to ECR
1.  In the ECR console, from the "View push commands" page, copy the commands to tag and push your image.
    *   **Tag your image**: `docker tag safebox-web:latest <aws_account_id>.dkr.ecr.<your-region>.amazonaws.com/safebox-web:latest`
    *   **Push your image**: `docker push <aws_account_id>.dkr.ecr.<your-region>.amazonaws.com/safebox-web:latest`
2.  Run these commands in your terminal.

### Step 6: Create an AWS App Runner Service
1.  Log in to the AWS Management Console and navigate to **AWS App Runner**.
2.  Click **"Create service"**.
3.  **Source and deployment**: Choose **"Container registry"**.
    *   **Provider**: Select **"Amazon ECR"**.
    *   **Repository**: Browse and select the `safebox-web` repository you pushed to ECR.
    *   **Image tag**: Enter `latest`.
    *   **Deployment trigger**: Choose **"Manual"** (or "Automatic" if you want App Runner to redeploy on new image pushes).
    *   Click **"Next"**.
4.  **Configure service**: 
    *   **Service name**: Enter `safebox-web-service`.
    *   **Port**: Enter `8000` (as configured in your Dockerfile and FastAPI app).
    *   **Environment variables**: Click **"Add environment variable"** and add your API key(s) from your `.env` file:
        *   `OPENAI_API_KEY` = `sk-your_openai_api_key` (or `ANTHROPIC_API_KEY`)
    *   **Security**: For `Instance role`, you can choose `Create new service role`.
    *   **Health check**: Set `Path` to `/` (or `/health` if you add a health endpoint to FastAPI).
    *   Click **"Next"**.
5.  **Review and create**: Review all settings and click **"Create deployment"**.

### Step 7: Obtain Live HTTPS URL
1.  Once the App Runner service is successfully deployed (this may take a few minutes), navigate to your `safebox-web-service` in the AWS App Runner console.
2.  The **Default domain** will be your live HTTPS URL (e.g., `https://<random-string>.<your-region>.awsapprunner.com`). Copy this URL.

### Step 8: Update Project Concept Note and Report
1.  Paste the obtained live AWS HTTPS URL into your `Project Concept Note` and `Project Report` documents where indicated.

By following these steps, your SafeBox Web application will be publicly accessible and running on AWS App Runner.
