# Configuration
$PROJECT_ID = "web-70a26"
$REGION = "asia-south1"

Write-Host "Deploying to Google App Engine..." -ForegroundColor Blue

# Create .env.yaml for App Engine environment variables
$envContent = "env_variables:`n  XAI_API_KEY: 'xai-fSzoJEPsV6AEduBGZkLOP449BOxRTWcZxhWjtYb6KzwMpQfhFBSHX7CMBIBXDKIzEes2Nsqiywn2olbu'"
Set-Content -Path ".env.yaml" -Value $envContent

try {
    # Deploy to App Engine
    Write-Host "Deploying application..." -ForegroundColor Blue
    gcloud app deploy app.yaml --quiet

    # Get the deployed URL
    $url = gcloud app browse --no-launch-browser
    
    Write-Host "`nDeployment completed successfully!" -ForegroundColor Green
    Write-Host "Your application is available at: $url" -ForegroundColor Green
    
} catch {
    Write-Host "Error during deployment: $_" -ForegroundColor Red
} finally {
    # Clean up sensitive files
    if (Test-Path ".env.yaml") {
        Remove-Item ".env.yaml"
    }
}
