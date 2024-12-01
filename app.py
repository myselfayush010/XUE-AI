from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)
CORS(app)

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
            'Authorization': f'Bearer {XAI_API_KEY}'
        }
        
        payload = {
            'messages': messages,
            'model': 'grok-beta',
            'stream': False,
            'temperature': 0.7
        }
        
        response = requests.post(XAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.getenv('PORT', 8080))
    
    # Run the app
    app.run(host='0.0.0.0', port=port)
