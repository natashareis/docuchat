#!/bin/bash

# Quick Deploy Script for Google Cloud Run

echo -e "\033[36mDocuChat Deployment to Google Cloud Run\033[0m"
echo -e "\033[36m========================================\033[0m"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "\033[31mERROR: gcloud CLI is not installed.\033[0m"
    echo -e "\033[33mPlease install it from: https://cloud.google.com/sdk/docs/install\033[0m"
    exit 1
fi

# Prompt for project ID
read -p "Enter your Google Cloud Project ID: " projectId
if [ -z "$projectId" ]; then
    echo -e "\033[31mERROR: Project ID is required\033[0m"
    exit 1
fi

# Prompt for Groq API Key
read -p "Enter your Groq API Key: " groqApiKey
if [ -z "$groqApiKey" ]; then
    echo -e "\033[31mERROR: Groq API Key is required\033[0m"
    exit 1
fi

# Prompt for CORS origins
read -p "Enter allowed CORS origins (comma-separated, e.g., https://yoursite.pages.dev): " corsOrigins
if [ -z "$corsOrigins" ]; then
    corsOrigins="http://localhost:5173"
fi

# Set the project
echo -e "\n\033[32mSetting project to $projectId...\033[0m"
gcloud config set project "$projectId"

# Enable required APIs
echo -e "\n\033[32mEnabling required APIs...\033[0m"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build the container
echo -e "\n\033[32mBuilding container image...\033[0m"
cd backend
gcloud builds submit --tag "gcr.io/$projectId/docuchat-backend"

if [ $? -ne 0 ]; then
    echo -e "\033[31mERROR: Build failed\033[0m"
    exit 1
fi

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)

# Deploy to Cloud Run with free tier protections
echo -e "\n\033[32mDeploying to Cloud Run with free tier limits...\033[0m"
gcloud run deploy docuchat-backend \
    --image "gcr.io/$projectId/docuchat-backend" \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --max-instances 10 \
    --concurrency 80 \
    --timeout 60s \
    --cpu 1 \
    --memory 512Mi \
    --set-env-vars "GROQ_API_KEY=$groqApiKey,DATABASE_URL=sqlite:///./app.db,BACKEND_CORS_ORIGINS=$corsOrigins,SECRET_KEY=$SECRET_KEY"

if [ $? -eq 0 ]; then
    echo -e "\n\033[32m========================================\033[0m"
    echo -e "\033[32mSUCCESS! Backend deployed to Cloud Run\033[0m"
    echo -e "\033[32m========================================\033[0m"
    echo -e "\n\033[36m🛡️  Free Tier Protection Active:\033[0m"
    echo -e "\033[37m  ✅ Request limit: 2,000,000/month\033[0m"
    echo -e "\033[37m  ✅ Max instances: 10\033[0m"
    echo -e "\033[37m  ✅ Auto-rejects requests after limit\033[0m"
    echo -e "\n\033[36mNext steps:\033[0m"
    echo -e "\033[37m1. Copy the service URL shown above\033[0m"
    echo -e "\033[37m2. Update frontend/.env.production with: VITE_API_URL=<your-service-url>\033[0m"
    echo -e "\033[37m3. Deploy frontend to Cloudflare Pages\033[0m"
    echo -e "\033[33m4. (Optional) Run ./setup-billing-protection.sh for budget alerts\033[0m"
    echo -e "\n\033[33mSee DEPLOYMENT.md for frontend deployment instructions\033[0m"
else
    echo -e "\n\033[31mERROR: Deployment failed\033[0m"
    exit 1
fi

cd ..
