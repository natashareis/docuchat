# 🚀 Quick Deployment Guide

## Prerequisites
1. **Groq API Key**: Get yours at [console.groq.com](https://console.groq.com/)
2. **Google Cloud Account**: Free tier available at [cloud.google.com](https://cloud.google.com/)
3. **Cloudflare Account**: Free at [cloudflare.com](https://cloudflare.com/)

---

## Option 1: One-Click Deploy (Easiest)

### Step 1: Backend (Google Cloud Run)

**Windows:**
```powershell
.\deploy-backend.ps1
```

**Mac/Linux:**
```bash
chmod +x deploy-backend.sh
./deploy-backend.sh
```

Follow the prompts:
- Enter your GCP Project ID
- Enter your Groq API Key
- Enter your Cloudflare Pages URL (or leave blank for now)

Copy the **Service URL** from the output (e.g., `https://docuchat-backend-xyz.run.app`)

### Step 2: Frontend (Cloudflare Pages)

1. Go to [Cloudflare Pages](https://dash.cloudflare.com/pages)
2. Click **"Create a project"** > **"Connect to Git"**
3. Select your GitHub repository
4. Configure:
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
   - **Root directory:** `frontend`
   - **Environment variable:** 
     - Name: `VITE_API_URL`
     - Value: `<paste your Cloud Run service URL>`
5. Click **"Save and Deploy"**

✅ **Done!** Your app is live!

---

## 🛡️ Free Tier Protection

Your deployment includes **automatic protection** to ensure you never pay:

- ✅ **Request limit:** Automatically stops at 2M requests/month
- ✅ **Resource limits:** Max 10 instances, 80 concurrent requests each
- ✅ **Auto-reset:** Counter resets on 1st of each month
- ✅ **Rate limit headers:** Track usage in real-time

**You cannot accidentally exceed the free tier.** See [FREE_TIER_PROTECTION.md](FREE_TIER_PROTECTION.md) for details.

Optional: Set up budget alerts:
```powershell
.\setup-billing-protection.ps1
```

---

## Option 2: GitHub Actions (Automated)

### Setup (One-time)

1. **Enable Google Cloud APIs:**
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```

2. **Create Service Account:**
   ```bash
   gcloud iam service-accounts create github-deployer \
     --display-name="GitHub Actions Deployer"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Add GitHub Secrets:**
   
   Go to your repo → Settings → Secrets and variables → Actions
   
   Add these secrets:
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: Contents of `key.json` file
   - `GROQ_API_KEY`: Your Groq API key
   - `CORS_ORIGINS`: Your Cloudflare Pages URL (e.g., `https://docuchat.pages.dev`)
   - `SECRET_KEY`: Generate with `openssl rand -hex 32`

4. **Deploy:** Just push to `main` branch!

---

## Option 3: Manual Deploy

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed manual deployment instructions.

---

## Free Tier Limits

### ✅ Google Cloud Run
- **Never sleeps** (pay-per-request model)
- 2 million requests/month free
- 360,000 GB-seconds memory free
- 180,000 vCPU-seconds free
- Perfect for low-to-medium traffic

### ✅ Cloudflare Pages
- **Unlimited bandwidth**
- Unlimited requests
- 500 builds/month
- Global CDN

---

## Update After Deployment

**Update CORS in Cloud Run:**

After you get your Cloudflare Pages URL, update the backend:

```bash
gcloud run services update docuchat-backend \
  --region us-central1 \
  --set-env-vars "BACKEND_CORS_ORIGINS=https://your-site.pages.dev"
```

**Custom Domain:**

Both Cloudflare Pages and Cloud Run support custom domains for free!

---

## Verify Deployment

1. **Backend:** Visit `https://your-backend-url.run.app` - should see:
   ```json
   {"message": "DocuChat AI API", "version": "1.0.0"}
   ```

2. **Frontend:** Visit your Cloudflare Pages URL and test:
   - Upload a document
   - Ask questions about it
   - Check sources display correctly

---

## Troubleshooting

**"gcloud not found":**
- Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install

**"Permission denied":**
- Run `gcloud auth login`
- Run `gcloud config set project YOUR_PROJECT_ID`

**CORS errors:**
- Update `BACKEND_CORS_ORIGINS` env var in Cloud Run
- Make sure to include `https://` in the URL

**Cold starts:**
- Free tier has 2-3 second cold starts after idle
- To eliminate: Set min instances to 1 (costs ~$5/month)

---

## Costs

With typical usage (hundreds of requests/day):

| Service | Cost |
|---------|------|
| Google Cloud Run | **$0** (within free tier) |
| Cloudflare Pages | **$0** (always free) |
| Groq API | **$0** (generous free tier) |
| **Total** | **$0/month** 🎉 |

Need help? Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guides!
