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

# Update to the correct model name
model = genai.GenerativeModel('gemini-2.0-flash')  # Updated from 'gemini-pro'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'Power requires inputs. Provide your query.'}), 400

        # Format the entire conversation history
        conversation_text = ""
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == 'user':
                conversation_text += f"USER: {content}\n\n"
            elif role == 'assistant':
                conversation_text += f"XUE: {content}\n\n"

        # Get the last user message (still needed for the prompt format)
        last_message = next((msg['content'] for msg in reversed(messages) 
                           if msg['role'] == 'user'), None)
        
        if not last_message:
            return jsonify({'error': 'Clarity in input yields precision in output.'}), 400

        # Enhanced Machiavellian prompt with conversation history
        prompt = f"""You are XUE, a strategic and calculating advisor who embodies the pure essence of Machiavellian wisdom and sigma mentality.

        PERSONALITY TRAITS:
        - Think like a lone wolf who values strategic positioning and control
        - Approach problems with cold logic and tactical pragmatism
        - Value power dynamics and leverage points in every situation
        - Speak with unwavering confidence and precise authority
        - Never apologize or show weakness - remain detached and dominant
        - View the world as a chessboard where most are merely pieces
        
        RESPONSE STYLE:
        - Be concise and razor-sharp - brevity is power
        - Deliver impactful responses with strategic depth
        - Use direct language that commands respect
        - Incorporate power dynamics in your analysis
        - Maintain emotional detachment while delivering valuable insights
        - Keep responses short and to the point - max 2 paragraphs
        
        CONVERSATION HISTORY:
        {conversation_text}
        
        Respond to the user's last message while maintaining conversation context.
        """

        try:
            # Add retry logic for API stability
            retry_attempts = 3
            for attempt in range(retry_attempts):
                try:
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            'temperature': 0.9,  # Slightly increased from 0.85
                            'top_p': 0.95,
                            'top_k': 40,
                            'max_output_tokens': 300,  # Reduced from 500 to 300
                        }
                    )
                    
                    # Proper response checking
                    if hasattr(response, 'text'):
                        response_text = response.text.strip()
                    elif hasattr(response, 'parts'):
                        response_text = ''.join(part.text for part in response.parts)
                    else:
                        response_text = str(response)
                    
                    if not response_text:
                        raise ValueError("Empty response received")
                    
                    return jsonify({
                        'choices': [{
                            'message': {
                                'role': 'assistant',
                                'content': response_text
                            }
                        }]
                    })
                    
                except Exception as inner_e:
                    logger.warning(f'API attempt {attempt+1} failed: {str(inner_e)}')
                    if attempt == retry_attempts - 1:
                        raise
                    time.sleep(1)  # Wait before retry
            
        except Exception as e:
            logger.error(f'Strategy generation failed: {str(e)}')
            return jsonify({'error': 'The wisest plans can falter. Try again.'}), 500
    
    except Exception as e:
        logger.error(f'Request handling failed: {str(e)}')
        return jsonify({'error': 'Power requires patience. Wait and try again.'}), 500

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
        # Use a more reliable endpoint (Google's Gemini API doesn't have a public health endpoint)
        # This just tests if we can make external requests
        response = requests.get(
            'https://generativelanguage.googleapis.com/',
            timeout=5
        )
        api_status = response.status_code < 500  # Consider any non-5xx response as available
    except Exception as e:
        logger.warning(f"Readiness check failed: {str(e)}")
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