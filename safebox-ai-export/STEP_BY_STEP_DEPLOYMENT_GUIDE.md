# Step-by-Step Deployment Guide for AI-Guard: SafeBox

This guide will walk you through deploying your AI-Guard: SafeBox application to AWS App Runner in simple, easy-to-follow steps.

## Prerequisites
Before you start, make sure you have:
- An AWS account (free tier eligible)
- AWS CLI installed on your computer
- Docker installed on your computer
- Your OpenAI API key OR Anthropic API key

---

## STEP 1: Get Your AWS Credentials

### 1.1 Sign in to AWS Console
1. Go to https://console.aws.amazon.com
2. Sign in with your AWS account

### 1.2 Create AWS Access Keys
1. Click on your account name in the top-right corner
2. Select **Security Credentials**
3. Scroll down to **Access keys**
4. Click **Create access key**
5. Choose **Command Line Interface (CLI)**
6. Accept the warning and click **Create access key**
7. **IMPORTANT:** Copy and save these two values:
   - **Access Key ID** (looks like: AKIA...)
   - **Secret Access Key** (long string of characters)

### 1.3 Note Your AWS Account ID and Region
1. Click on your account name in the top-right
2. Your **Account ID** is shown (12 digits)
3. Choose a **Region** (e.g., us-east-1, us-west-2)
   - Recommendation: Use **us-east-1** for lowest latency in North America

**Save these values:**
```
AWS Account ID: _______________
AWS Region: _______________
Access Key ID: _______________
Secret Access Key: _______________
```

---

## STEP 2: Configure AWS CLI on Your Computer

### 2.1 Open Terminal/Command Prompt
- **Mac/Linux:** Open Terminal
- **Windows:** Open Command Prompt or PowerShell

### 2.2 Configure AWS CLI
Run this command:
```bash
aws configure
```

When prompted, enter:
1. **AWS Access Key ID:** Paste your Access Key ID
2. **AWS Secret Access Key:** Paste your Secret Access Key
3. **Default region name:** Enter your region (e.g., us-east-1)
4. **Default output format:** Press Enter (leave blank)

### 2.3 Verify Configuration
Run:
```bash
aws sts get-caller-identity
```
You should see your Account ID and user information.

---

## STEP 3: Prepare Your API Key

### 3.1 Choose Your LLM Provider
You need ONE of these:

**Option A: OpenAI (GPT-4o)**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with sk-proj-)
4. Save it securely

**Option B: Anthropic (Claude 3.5 Sonnet)**
1. Go to https://console.anthropic.com/keys
2. Click "Create Key"
3. Copy the key (starts with sk-ant-)
4. Save it securely

**Save this value:**
```
LLM API Key: _______________
```

---

## STEP 4: Build the Docker Image Locally

### 4.1 Navigate to Project Directory
```bash
cd /path/to/safebox-web
```
(Replace with your actual project path)

### 4.2 Build Docker Image
```bash
docker build -t safebox-web:latest .
```
Wait for this to complete (2-5 minutes)

### 4.3 Verify Image Built Successfully
```bash
docker images | grep safebox-web
```
You should see your image listed

---

## STEP 5: Create Amazon ECR Repository

### 5.1 Go to AWS ECR Console
1. Go to https://console.aws.amazon.com/ecr/
2. Click **Create repository**
3. Enter repository name: `safebox-web`
4. Leave other settings as default
5. Click **Create repository**

### 5.2 Note Your ECR Repository URI
The repository page will show a URI like:
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/safebox-web
```
**Save this:**
```
ECR Repository URI: _______________
```

---

## STEP 6: Push Docker Image to ECR

### 6.1 Authenticate Docker to ECR
In your terminal, run:
```bash
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com
```
Replace:
- `YOUR_REGION` with your region (e.g., us-east-1)
- `YOUR_ACCOUNT_ID` with your 12-digit account ID

### 6.2 Tag Your Docker Image
```bash
docker tag safebox-web:latest YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/safebox-web:latest
```

### 6.3 Push Image to ECR
```bash
docker push YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/safebox-web:latest
```
Wait for this to complete (2-10 minutes depending on image size)

### 6.4 Verify Upload
1. Go back to AWS ECR Console
2. Click on `safebox-web` repository
3. You should see your image listed with tag `latest`

---

## STEP 7: Create AWS App Runner Service

### 7.1 Go to AWS App Runner Console
1. Go to https://console.aws.amazon.com/apprunner/
2. Click **Create service**

### 7.2 Configure Source
1. **Source:** Select "Container registry"
2. **Provider:** Select "Amazon ECR"
3. **Repository:** Click "Browse" and select `safebox-web`
4. **Image tag:** Enter `latest`
5. **Deployment trigger:** Select "Manual"
6. Click **Next**

### 7.3 Configure Service
1. **Service name:** Enter `safebox-web-service`
2. **Port:** Enter `8000`
3. **Environment variables:** Click "Add environment variable"
   - **Key:** `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
   - **Value:** Paste your API key
4. Click **Next**

### 7.4 Review and Create
1. Review all settings
2. Click **Create & deploy**
3. Wait for deployment (5-10 minutes)

### 7.5 Get Your Live URL
1. Once deployment completes, you'll see a green checkmark
2. Look for **Default domain** - this is your live URL
3. It will look like: `https://xxxxxxxxxx.us-east-1.awsapprunner.com`

**Save this:**
```
Live Application URL: _______________
```

---

## STEP 8: Test Your Live Application

### 8.1 Open Your Application
1. Copy your live URL from Step 7.5
2. Paste it into your browser
3. You should see the AI-Guard: SafeBox dashboard

### 8.2 Test the Application
1. Enter a URL in the input field (e.g., https://www.google.com)
2. Click "Analyze"
3. You should see:
   - Loading indicator
   - Tier 1 fast check results
   - Tier 2 AI analysis streaming in real-time
4. Try a suspicious URL to see the warning

---

## STEP 9: Update Your Documentation

### 9.1 Update Concept Note
1. Open `concept_note.md` in a text editor
2. Find the line: `Live AWS Application URL`
3. Replace with your actual URL:
   ```
   Live AWS Application URL: https://xxxxxxxxxx.us-east-1.awsapprunner.com
   ```
4. Save the file

### 9.2 Regenerate PDF
1. Open terminal
2. Run:
   ```bash
   manus-md-to-pdf concept_note.md Project_Concept_Note_AI_Guard_SafeBox.pdf
   ```

### 9.3 Update Project Report
1. Open `project_report.md`
2. Find the section mentioning live URL
3. Add your URL where indicated
4. Save the file

### 9.4 Regenerate Report PDF
```bash
manus-md-to-pdf project_report.md Project_Report_AI_Guard_SafeBox.pdf
```

---

## STEP 10: Prepare Final Submission

### 10.1 Collect All Files
Create a folder with these files:
- `Project_Concept_Note_AI_Guard_SafeBox.pdf` (updated with live URL)
- `Project_Report_AI_Guard_SafeBox.pdf` (updated with live URL)
- `main.py`
- `requirements.txt`
- `Dockerfile`
- `.env.example`
- `static/index.html`
- `static/style.css`
- `static/script.js`
- `aws_deployment_instructions.md`

### 10.2 Create a README
Create a file called `README.md` with:
```markdown
# AI-Guard: SafeBox

## Live Application
[Your Live URL Here]

## Project Description
AI-Guard: SafeBox is an AI-powered URL safety analyzer that protects users from phishing attacks.

## Features
- Two-tier analysis (fast check + AI deep analysis)
- Real-time streaming results
- Responsive design
- Secure API key management

## Deployment
See `aws_deployment_instructions.md` for deployment details.
```

### 10.3 Submit Your Project
1. Compress all files into a ZIP file
2. Submit to your course platform or assignment portal
3. Include your live URL in the submission notes

---

## Troubleshooting

### Docker Build Fails
- Make sure Docker is running
- Check that you're in the correct directory
- Run: `docker --version` to verify installation

### ECR Push Fails
- Verify AWS credentials are configured: `aws sts get-caller-identity`
- Check region is correct in push command
- Ensure ECR repository exists

### App Runner Deployment Fails
- Check environment variables are set correctly
- Verify port is 8000
- Check API key is valid and has correct format

### Application Not Working
- Check live URL is correct
- Wait 2-3 minutes after deployment
- Check browser console for errors (F12)
- Verify API key has credits/quota

---

## Summary

You've successfully:
1. ✅ Created AWS credentials
2. ✅ Configured AWS CLI
3. ✅ Built Docker image
4. ✅ Created ECR repository
5. ✅ Pushed image to ECR
6. ✅ Created App Runner service
7. ✅ Got live HTTPS URL
8. ✅ Tested application
9. ✅ Updated documentation
10. ✅ Prepared submission

**Your AI-Guard: SafeBox is now live and ready for submission!**
