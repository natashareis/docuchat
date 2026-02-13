# Deployment Guide

This guide covers deploying DocuChat with **Cloudflare Pages** (frontend) and **Google Cloud Run** (backend).

## Prerequisites

1. [Google Cloud account](https://cloud.google.com/) (free tier)
2. [Cloudflare account](https://cloudflare.com/)
3. [Groq API key](https://console.groq.com/)

## Backend Deployment (Google Cloud Run)

### Option 1: Using gcloud CLI (Recommended)

1. **Install Google Cloud SDK:**
   ```bash
   # Download from https://cloud.google.com/sdk/docs/install
   ```

2. **Login and set project:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs:**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

4. **Build and deploy:**
   ```bash
   cd backend
   
   # Build the container
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/docuchat-backend
   
   # Deploy to Cloud Run
   gcloud run deploy docuchat-backend \
     --image gcr.io/YOUR_PROJECT_ID/docuchat-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "GROQ_API_KEY=your-groq-api-key,DATABASE_URL=sqlite:///./app.db"
   ```

5. **Note the service URL** (e.g., `https://docuchat-backend-xyz.run.app`)

### Option 2: Using Google Cloud Console UI

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click "Create Service"
3. Click "Continuously deploy from a repository" > "Set up with Cloud Build"
4. Connect your GitHub repo
5. Select `backend/Dockerfile`
6. Set environment variables:
   - `GROQ_API_KEY`: your Groq API key
   - `DATABASE_URL`: `sqlite:///./app.db`
7. Click "Create"

### Storage Configuration

For persistent file uploads and vector database:

```bash
# Create a bucket for storage
gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=us-central1

# Mount to Cloud Run (in deployment command):
gcloud run deploy docuchat-backend \
  --execution-environment gen2 \
  --set-env-vars "CHROMA_PERSIST_DIRECTORY=/mnt/data/chroma_data,UPLOAD_DIR=/mnt/data/uploads"
```

Note: Free tier has 5GB storage. For production, consider Google Cloud Storage.

## Frontend Deployment (Cloudflare Pages)

### Option 1: Using Cloudflare Dashboard (Easiest)

1. Go to [Cloudflare Pages](https://dash.cloudflare.com/pages)
2. Click "Create a project" > "Connect to Git"
3. Select your repository
4. Configure build settings:
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
   - **Root directory:** `frontend`
5. Add environment variable:
   - `VITE_API_URL`: Your Cloud Run backend URL (e.g., `https://docuchat-backend-xyz.run.app`)
6. Click "Save and Deploy"

### Option 2: Using Wrangler CLI

1. **Install Wrangler:**
   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare:**
   ```bash
   wrangler login
   ```

3. **Deploy:**
   ```bash
   cd frontend
   
   # Update API URL in .env.production
   echo "VITE_API_URL=https://your-backend-url.run.app" > .env.production
   
   # Build and deploy
   npm run build
   wrangler pages deploy dist --project-name=docuchat
   ```

## Update Frontend API URL

Edit `frontend/.env.production`:

```env
VITE_API_URL=https://your-cloud-run-backend-url.run.app
```

Or set it in Cloudflare Pages environment variables.

## CORS Configuration

The backend needs to allow requests from your Cloudflare Pages domain. Update `backend/app/main.py`:

```python
origins = [
    "https://your-site.pages.dev",
    "https://docuchat.yourdomain.com",  # If using custom domain
]
```

## Free Tier Limits

### Google Cloud Run (Free Tier)
- ✅ **Never sleeps** - pay per request
- 2 million requests/month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds
- 1 GB outbound network/month

### Cloudflare Pages (Free Tier)
- ✅ Unlimited bandwidth
- Unlimited requests
- 500 builds/month
- 100 custom domains

## Monitoring

View logs:
```bash
# Backend logs
gcloud run logs tail docuchat-backend --region us-central1

# Or in console
https://console.cloud.google.com/run
```

## Custom Domain (Optional)

### Cloudflare Pages:
1. Go to your Pages project > Custom domains
2. Add your domain
3. Update DNS records as instructed

### Cloud Run:
1. Go to Cloud Run service > "Manage Custom Domains"
2. Add domain and verify
3. Update DNS records

## Alternative: Oracle Cloud Free Tier

If you prefer an always-on VM (no cold starts):

1. Sign up for [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Create a Compute Instance (Ampere A1 - 4 cores, 24GB RAM free)
3. Install Docker:
   ```bash
   sudo yum install docker -y
   sudo systemctl start docker
   ```
4. Run your backend:
   ```bash
   docker run -d -p 80:8080 \
     -e GROQ_API_KEY=your-key \
     -v /data/chroma:/app/chroma_data \
     -v /data/uploads:/app/uploads \
     your-backend-image
   ```

This gives you a true always-on server (never sleeps) but requires more DevOps.

## Troubleshooting

**Cloud Run cold starts:**
- First request after idle may take 2-3 seconds
- Set minimum instances to 1 (costs ~$5/month) to avoid cold starts:
  ```bash
  gcloud run services update docuchat-backend --min-instances 1
  ```

**Storage persistence:**
- Use Google Cloud Storage buckets for production
- SQLite works for demo/small scale
- Consider Cloud SQL for production database

**Environment variables:**
- Never commit `.env` files
- Use Cloud Run environment variables or Secret Manager
