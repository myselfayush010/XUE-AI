from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import socket
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)

# Cloud Run automatically handles SSL and proxying
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Configure CORS for Cloud Run
CORS(app, resources={
    r"/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
})

# Configure session settings
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Get API key from environment variable
XAI_API_KEY = os.getenv('XAI_API_KEY')
if not XAI_API_KEY:
    raise ValueError("XAI_API_KEY environment variable is not set")

XAI_API_URL = 'https://api.x.ai/v1/chat/completions'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {XAI_API_KEY}',
            'Connection': 'keep-alive'
        }
        
        payload = {
            'messages': messages,
            'model': 'grok-beta',
            'stream': False,
            'temperature': 0.7
        }
        
        # Add timeout and better error handling
        response = requests.post(
            XAI_API_URL, 
            headers=headers, 
            json=payload,
            timeout=30,  # 30 seconds timeout
            verify=True  # Ensure SSL verification
        )
        
        if response.status_code == 408:  # Request Timeout
            return jsonify({'error': 'Request timed out'}), 408
        elif response.status_code == 502:  # Bad Gateway
            return jsonify({'error': 'Bad gateway error'}), 502
        elif response.status_code == 504:  # Gateway Timeout
            return jsonify({'error': 'Gateway timeout'}), 504
            
        response.raise_for_status()
        return jsonify(response.json())
    
    except requests.exceptions.Timeout:
        return jsonify({'error': 'The request timed out'}), 408
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error occurred'}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/_ah/warmup')
def warmup():
    """Handle Cloud Run warmup requests."""
    return '', 200

@app.route('/health')
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/readiness')
def readiness_check():
    # Check if we can connect to the x.ai API
    try:
        response = requests.get(
            'https://api.x.ai/health',  # Replace with actual health endpoint if different
            timeout=5
        )
        api_status = response.status_code == 200
    except:
        api_status = False

    status = {
        'status': 'ready' if api_status else 'not_ready',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': {
            'x_ai_api': 'up' if api_status else 'down'
        }
    }
    return jsonify(status), 200 if api_status else 503

if __name__ == '__main__':
    # Get port from environment variable (Cloud Run sets this automatically)
    port = int(os.getenv('PORT', 8080))
    
    # Cloud Run handles HTTPS automatically
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
