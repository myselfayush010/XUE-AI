from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)

# Configure retries for requests
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=0.3,  # wait 0.3s * (2 ** (retry - 1)) between retries
    status_forcelist=[408, 429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
})

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
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Keep-Alive': 'timeout=65, max=100'
        }
        
        payload = {
            'messages': messages,
            'model': 'grok-beta',
            'stream': False,
            'temperature': 0.7
        }
        
        # Use session with retry mechanism
        start_time = time.time()
        response = http.post(
            XAI_API_URL,
            headers=headers,
            json=payload,
            timeout=(5, 30),  # (connect timeout, read timeout)
            verify=True
        )
        
        # Log response time
        elapsed_time = time.time() - start_time
        app.logger.info(f'API request completed in {elapsed_time:.2f} seconds')
        
        # Check response status
        if response.status_code >= 400:
            error_msg = f'API error: {response.status_code}'
            try:
                error_msg = response.json().get('error', error_msg)
            except:
                pass
            return jsonify({'error': error_msg}), response.status_code
            
        return jsonify(response.json())
    
    except requests.exceptions.ConnectTimeout:
        return jsonify({'error': 'Connection timed out while trying to reach the server'}), 504
    except requests.exceptions.ReadTimeout:
        return jsonify({'error': 'Server took too long to respond'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Failed to establish connection with the server'}), 503
    except requests.exceptions.RequestException as e:
        app.logger.error(f'Request failed: {str(e)}')
        return jsonify({'error': 'An error occurred while processing your request'}), 500
    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

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
    
    # Cloud Run handles HTTPS automatically
    app.run(
        host='0.0.0.0',
        port=8080
    )
