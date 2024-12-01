# Configuration
$PROJECT_ID = "web-70a26"
$REGION = "asia-south1"
$APP_NAME = "chat-app"
$IMAGE_NAME = "gcr.io/${PROJECT_ID}/${APP_NAME}"

# Functions for colored output
function Write-BlueOutput { param($Text) Write-Host $Text -ForegroundColor Blue }
function Write-GreenOutput { param($Text) Write-Host $Text -ForegroundColor Green }

Write-BlueOutput "Choose deployment method:"
Write-Host "1) Docker Image"
Write-Host "2) GitHub Repository"
$choice = Read-Host "Enter choice (1 or 2)"

switch ($choice) {
    "1" {
        try {
            Write-BlueOutput "Building and deploying using Docker..."
            
            # Build the Docker image
            Write-BlueOutput "Building Docker image..."
            docker build -t $IMAGE_NAME .
            
            # Configure Docker for Google Cloud
            Write-BlueOutput "Configuring Docker for Google Cloud..."
            gcloud auth configure-docker
            
            # Push the image
            Write-BlueOutput "Pushing image to Google Container Registry..."
            docker push $IMAGE_NAME
            
            # Deploy to Cloud Run
            Write-BlueOutput "Deploying to Cloud Run..."
            $API_KEY = Get-Content .env.prod | Where-Object { $_ -match "XAI_API_KEY=" } | ForEach-Object { $_.Split('=')[1] }
            
            gcloud run deploy $APP_NAME `
                --image $IMAGE_NAME `
                --platform managed `
                --region $REGION `
                --allow-unauthenticated `
                --set-env-vars "XAI_API_KEY=$API_KEY"
            
            Write-GreenOutput "Deployment complete! Your app should be available at the URL shown above."
        }
        catch {
            Write-Host "Error occurred during deployment: $_" -ForegroundColor Red
            exit 1
        }
    }
    "2" {
        Write-BlueOutput "Setting up GitHub repository..."
        
        # Initialize git if not already initialized
        if (-not (Test-Path .git)) {
            git init
            git add .
            git commit -m "Initial commit"
        }
        
        Write-GreenOutput "`nNext steps for GitHub deployment:"
        Write-Host "1. Create a new repository on GitHub"
        Write-Host "2. Run these commands:"
        Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
        Write-Host "   git push -u origin main"
        Write-Host "3. In Google Cloud Console:"
        Write-Host "   - Go to Cloud Run"
        Write-Host "   - Click 'Create Service'"
        Write-Host "   - Choose 'Continuously deploy new revisions from a source repository'"
        Write-Host "   - Connect your GitHub repository"
        Write-Host "   - Add XAI_API_KEY in the environment variables section"
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}
