# Configuration
$PROJECT_ID = "elite-fabric-443322-e1"
$REGION = "asia-south2"  # Delhi region
$SERVICE_NAME = "chat-app"

Write-Host "Preparing Cloud Run deployment via GitHub..." -ForegroundColor Blue

# Enable necessary APIs
Write-Host "Enabling necessary Google Cloud APIs..." -ForegroundColor Blue
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretsmanager.googleapis.com

# Initialize git if not already initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Blue
    git init
    git add .
    git commit -m "Initial commit"
}

Write-Host "`nNext Steps for Deployment:" -ForegroundColor Green
Write-Host "1. Create a new GitHub repository (DO NOT initialize with README)"
Write-Host "   Go to: https://github.com/new"

Write-Host "`n2. Run these Git commands:" -ForegroundColor Yellow
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/$SERVICE_NAME.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"

Write-Host "`n3. Go to Google Cloud Console:" -ForegroundColor Yellow
Write-Host "   https://console.cloud.google.com/run"
Write-Host "   a. Click 'CREATE SERVICE'"
Write-Host "   b. Choose 'asia-south2 (Delhi)' as region"
Write-Host "   c. Select 'Continuously deploy new revisions from a source repository'"
Write-Host "   d. Click 'SET UP WITH CLOUD BUILD'"
Write-Host "   e. Connect your GitHub repository"
Write-Host "   f. Select 'main' branch"

Write-Host "`n4. Configure deployment settings:" -ForegroundColor Yellow
Write-Host "   - Region: asia-south2 (Delhi)"
Write-Host "   - CPU allocation: CPU is only allocated during request processing"
Write-Host "   - Memory: 512 MiB (minimum)"
Write-Host "   - Request timeout: 300 seconds"
Write-Host "   - Minimum instances: 0"
Write-Host "   - Maximum instances: 1"
Write-Host "   - Ingress: Allow all traffic"

Write-Host "`n5. Add environment variables:" -ForegroundColor Yellow
Write-Host "   Name: XAI_API_KEY"
Write-Host "   Value: [Your API Key from .env file]"

Write-Host "`nImportant Notes:" -ForegroundColor Cyan
Write-Host "- Service will be deployed in Delhi region (asia-south2)"
Write-Host "- The service will scale to zero when not in use (cost-effective)"
Write-Host "- First request might be slow (cold start)"
Write-Host "- You can monitor the service in Cloud Console"

Write-Host "`nEstimated Free Tier Usage:" -ForegroundColor Cyan
Write-Host "- 2 million requests per month"
Write-Host "- 360,000 GB-seconds of memory"
Write-Host "- 180,000 vCPU-seconds of compute time"
Write-Host "- 1 GB network egress from North America"
