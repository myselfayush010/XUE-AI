#  AI Chat Assistant   Simple Focused No History

A responsive chat application powered by Gemini's API, designed specifically for students. The application works seamlessly on both mobile and desktop devices.

## Features

- Responsive design that adapts to both mobile and desktop
- Real-time chat interface with x.ai's powerful AI model
- Clean and intuitive user interface
- Secure API key handling
- Educational focus for student interactions

## Local Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the `.env` file with your x.ai API key:
```
XAI_API_KEY=your-api-key
```

3. Run the application locally:
```bash
python app.py
```

## Google Cloud Deployment

### Prerequisites

1. Install Google Cloud SDK
2. Initialize Google Cloud SDK and set your project:
```bash
gcloud init
```

### Deployment Steps

1. Edit the `deploy.sh` script:
   - Set your `PROJECT_ID`
   - Set your preferred `REGION`

2. Make the deploy script executable:
```bash
chmod +x deploy.sh
```

3. Run the deployment:
```bash
./deploy.sh
```

The script will:
- Create a Secret Manager secret for your API key
- Build and push the Docker container
- Deploy to Cloud Run
- Set up environment variables securely
- Display the deployed application URL

### Manual Deployment

If you prefer to deploy manually:

1. Create secret:
```bash
gcloud secrets create xai-api-key --replication-policy="automatic" --data-file=".env.prod"
```

2. Build container:
```bash
gcloud builds submit --tag gcr.io/[PROJECT-ID]/chat-app
```

3. Deploy to Cloud Run:
```bash
gcloud run deploy chat-app \
  --image gcr.io/[PROJECT-ID]/chat-app \
  --platform managed \
  --region [REGION] \
  --allow-unauthenticated \
  --set-secrets "XAI_API_KEY=xai-api-key:latest"
```

## Security

- API key is stored securely in Google Cloud Secret Manager
- CORS protection enabled
- Input sanitization implemented
- Secure error handling
- HTTPS enforced
- Non-root user in Docker

## Scaling

The application is configured to scale automatically based on:
- CPU utilization (target: 65%)
- Request latency
- Number of concurrent requests

## Monitoring

Monitor your application in Google Cloud Console:
- Cloud Run dashboard
- Cloud Logging
- Cloud Monitoring
- Error Reporting
