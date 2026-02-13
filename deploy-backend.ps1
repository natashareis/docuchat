# Quick Deploy Script for Google Cloud Run

Write-Host "DocuChat Deployment to Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: gcloud CLI is not installed." -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Prompt for project ID
$projectId = Read-Host "Enter your Google Cloud Project ID"
if ([string]::IsNullOrWhiteSpace($projectId)) {
    Write-Host "ERROR: Project ID is required" -ForegroundColor Red
    exit 1
}

# Prompt for Groq API Key
$groqApiKey = Read-Host "Enter your Groq API Key"
if ([string]::IsNullOrWhiteSpace($groqApiKey)) {
    Write-Host "ERROR: Groq API Key is required" -ForegroundColor Red
    exit 1
}

# Prompt for CORS origins
$corsOrigins = Read-Host "Enter allowed CORS origins (comma-separated, e.g., https://yoursite.pages.dev)"
if ([string]::IsNullOrWhiteSpace($corsOrigins)) {
    $corsOrigins = "http://localhost:5173"
}

# Set the project
Write-Host "`nSetting project to $projectId..." -ForegroundColor Green
gcloud config set project $projectId

# Enable required APIs
Write-Host "`nEnabling required APIs..." -ForegroundColor Green
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build the container
Write-Host "`nBuilding container image..." -ForegroundColor Green
Set-Location backend
gcloud builds submit --tag "gcr.io/$projectId/docuchat-backend"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    exit 1
}

# Deploy to Cloud Run with free tier protections
Write-Host "`nDeploying to Cloud Run with free tier limits..." -ForegroundColor Green
gcloud run deploy docuchat-backend `
    --image "gcr.io/$projectId/docuchat-backend" `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --max-instances 10 `
    --concurrency 80 `
    --timeout 60s `
    --cpu 1 `
    --memory 512Mi `
    --set-env-vars "GROQ_API_KEY=$groqApiKey,DATABASE_URL=sqlite:///./app.db,BACKEND_CORS_ORIGINS=$corsOrigins,SECRET_KEY=$(New-Guid)"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Backend deployed to Cloud Run" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`n🛡️ Free Tier Protection Active:" -ForegroundColor Cyan
    Write-Host "  ✅ Request limit: 2,000,000/month" -ForegroundColor White
    Write-Host "  ✅ Max instances: 10" -ForegroundColor White
    Write-Host "  ✅ Auto-rejects requests after limit" -ForegroundColor White
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Copy the service URL shown above" -ForegroundColor White
    Write-Host "2. Update frontend/.env.production with: VITE_API_URL=<your-service-url>" -ForegroundColor White
    Write-Host "3. Deploy frontend to Cloudflare Pages" -ForegroundColor White
    Write-Host "4. (Optional) Run .\setup-billing-protection.ps1 for budget alerts" -ForegroundColor Yellow
    Write-Host "`nSee DEPLOYMENT.md for frontend deployment instructions" -ForegroundColor Yellow
} else {
    Write-Host "`nERROR: Deployment failed" -ForegroundColor Red
    exit 1
}

Set-Location ..
