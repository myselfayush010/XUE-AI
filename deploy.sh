#!/bin/bash

# Configuration
PROJECT_ID="web-70a26"        # Google Cloud project ID
REGION="asia-south1"          # Mumbai region for best performance in India
APP_NAME="chat-app"
SECRET_NAME="xai-api-key"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting deployment process...${NC}"

# 1. Create Secret in Secret Manager
echo -e "${BLUE}Creating secret in Secret Manager...${NC}"
gcloud secrets create $SECRET_NAME \
    --replication-policy="automatic" \
    --data-file=".env.prod" || true

# 2. Build the container
echo -e "${BLUE}Building container...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME

# 3. Deploy to Cloud Run
echo -e "${BLUE}Deploying to Cloud Run...${NC}"
gcloud run deploy $APP_NAME \
    --image gcr.io/$PROJECT_ID/$APP_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-secrets "XAI_API_KEY=$SECRET_NAME:latest"

# 4. Get the URL
echo -e "${BLUE}Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $APP_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Your application is available at: ${SERVICE_URL}${NC}"
