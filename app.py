from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
else:
    logger.warning("No .env file found")

app = Flask(__name__)

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
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        # Convert messages to Gemini format
        # Assuming messages are in the format [{"role": "user", "content": "..."}, ...]
        history = []
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == 'user':
                history.append(content)
            elif role == 'assistant':
                history.append(content)

        start_time = time.time()
        
        try:
            # Generate response using Gemini
            response = model.generate_content(
                history[-1] if history else "",  # Use the last message
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            # Format response to match expected structure
            response_data = {
                'choices': [{
                    'message': {
                        'role': 'assistant',
                        'content': response.text
                    }
                }]
            }
            
            elapsed_time = time.time() - start_time
            app.logger.info(f'API request completed in {elapsed_time:.2f} seconds')
            
            return jsonify(response_data)
            
        except Exception as e:
            app.logger.error(f'Gemini API error: {str(e)}')
            return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/_ah/warmup')
def warmup():
    """Handle Cloud Run warmup requests."""
    return '', 200

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/readiness')
def readiness_check():
    # Check if we can connect to the Gemini API
    try:
        response = requests.get(
            'https://api.google.com/health',  # Replace with actual health endpoint if different
            timeout=5
        )
        api_status = response.status_code == 200
    except:
        api_status = False

    status = {
        'status': 'ready' if api_status else 'not_ready',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': {
            'gemini_api': 'up' if api_status else 'down'
        }
    }
    return jsonify(status), 200 if api_status else 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port)