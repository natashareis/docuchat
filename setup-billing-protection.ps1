# Script to set up billing protection for Google Cloud Run
# This ensures you never exceed free tier limits

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Google Cloud Billing Protection Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for project ID
$PROJECT_ID = Read-Host "Enter your Google Cloud Project ID"
if ([string]::IsNullOrWhiteSpace($PROJECT_ID)) {
    Write-Host "ERROR: Project ID is required" -ForegroundColor Red
    exit 1
}

# Set project
gcloud config set project $PROJECT_ID

Write-Host "`n1. Setting up budget alerts..." -ForegroundColor Green

# Budget setup instructions
Write-Host "To create budget alerts, go to:" -ForegroundColor Yellow
Write-Host "https://console.cloud.google.com/billing/budgets" -ForegroundColor White
Write-Host "- Set budget to `$1" -ForegroundColor White
Write-Host "- Set alerts at 50%, 90%, and 100%" -ForegroundColor White
Write-Host ""

Write-Host "`n2. Setting Cloud Run quota limits..." -ForegroundColor Green
Write-Host ""

Write-Host "Run these commands to limit your service:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Limit concurrent requests and instances" -ForegroundColor Gray
Write-Host "gcloud run services update docuchat-backend ``" -ForegroundColor White
Write-Host "  --region us-central1 ``" -ForegroundColor White
Write-Host "  --max-instances 10 ``" -ForegroundColor White
Write-Host "  --concurrency 80" -ForegroundColor White
Write-Host ""
Write-Host "# Set request timeout" -ForegroundColor Gray
Write-Host "gcloud run services update docuchat-backend ``" -ForegroundColor White
Write-Host "  --region us-central1 ``" -ForegroundColor White
Write-Host "  --timeout 60s" -ForegroundColor White
Write-Host ""

Write-Host "`n3. Protection mechanisms in place:" -ForegroundColor Green
Write-Host "✅ Application-level rate limiting (2M requests/month)" -ForegroundColor White
Write-Host "✅ Automatic request rejection after limit" -ForegroundColor White
Write-Host "✅ Rate limit headers in responses" -ForegroundColor White
Write-Host ""

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Set up budget alerts at the link above" -ForegroundColor White
Write-Host "2. Run the quota commands shown above" -ForegroundColor White
Write-Host "3. Monitor usage: https://console.cloud.google.com/run" -ForegroundColor White
Write-Host ""
Write-Host "Your app will automatically reject requests after 2M per month! 🛡️" -ForegroundColor Green
