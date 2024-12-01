#!/bin/bash

# Configuration
PROJECT_ID="web-70a26"
REGION="asia-south1"
APP_NAME="chat-app"
SECRET_NAME="xai-api-key"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to deploy using Docker
deploy_docker() {
    echo -e "${BLUE}Building and deploying using Docker...${NC}"
    
    # Build the container
    docker build -t gcr.io/$PROJECT_ID/$APP_NAME .
    
    # Push to Container Registry
    docker push gcr.io/$PROJECT_ID/$APP_NAME
    
    # Deploy to Cloud Run
    gcloud run deploy $APP_NAME \
        --image gcr.io/$PROJECT_ID/$APP_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars "XAI_API_KEY=$(cat .env.prod | grep XAI_API_KEY | cut -d '=' -f2)"
}

# Function to set up GitHub deployment
setup_github() {
    echo -e "${BLUE}Setting up GitHub repository...${NC}"
    
    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit"
    fi
    
    # Instructions for GitHub
    echo -e "${GREEN}Next steps for GitHub deployment:${NC}"
    echo "1. Create a new repository on GitHub"
    echo "2. Run these commands:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
    echo "   git push -u origin main"
    echo "3. In Google Cloud Console:"
    echo "   - Go to Cloud Run"
    echo "   - Click 'Create Service'"
    echo "   - Choose 'Continuously deploy new revisions from a source repository'"
    echo "   - Connect your GitHub repository"
    echo "   - Add XAI_API_KEY in the environment variables section"
}

# Ask user which deployment method to use
echo "Choose deployment method:"
echo "1) Docker Image"
echo "2) GitHub Repository"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        deploy_docker
        ;;
    2)
        setup_github
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo -e "${GREEN}Setup complete!${NC}"
