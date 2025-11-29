"""Main Flask API application"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import os
import sys

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for frontend access

# Configuration
MODEL_PATH = os.environ.get('MODEL_PATH', 'models/llama-3.2-3b-q4.gguf')
USE_OLLAMA = os.environ.get('USE_OLLAMA', 'false').lower() == 'true'

# Auto-detect: Use Ollama on macOS for local development, llama-cpp-python in Docker
if sys.platform == 'darwin' and not os.path.exists('/.dockerenv'):
    # Running on macOS locally - use Ollama
    USE_OLLAMA = True
    print("🍎 Detected macOS - using Ollama for local development")

# Load appropriate inference engine
print("Initializing LLM service...")
try:
    if USE_OLLAMA:
        from inference_ollama import LLMInference
        llm = LLMInference()
        MODEL_NAME = "ollama:codellama:7b-instruct"
        print("✅ Using Ollama inference engine")
    else:
        from inference import LLMInference
        llm = LLMInference(MODEL_PATH)
        MODEL_NAME = os.path.basename(MODEL_PATH)
        print("✅ Using llama-cpp-python inference engine")
except ImportError as e:
    print(f"❌ Error loading inference engine: {e}")
    print("📝 Falling back to mock inference for testing")
    from inference_mock import LLMInference
    llm = LLMInference(MODEL_PATH)
    MODEL_NAME = f"mock:{os.path.basename(MODEL_PATH)}"
except Exception as e:
    print(f"❌ Error initializing LLM: {e}")
    raise

print("Service ready!")

# Metrics
stats = {
    'total_requests': 0,
    'total_tokens': 0,
    'total_latency': 0.0
}

@app.route('/')
def index():
    """Serve frontend HTML"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Kubernetes"""
    return jsonify({
        'status': 'healthy',
        'model': MODEL_NAME
    }), 200

@app.route('/chat', methods=['POST'])
def chat():
    """Main inference endpoint"""
    start_time = time.time()

    try:
        # Parse request
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt field'}), 400

        prompt = data['prompt']
        max_tokens = data.get('max_tokens', 150)
        temperature = data.get('temperature', 0.7)
        prompt = f"[INST] {prompt} [/INST]"
       


        # Generate response
        response = llm.generate(prompt, max_tokens, temperature)

        # Calculate metrics
        latency = time.time() - start_time
        tokens_generated = response['usage']['completion_tokens']

        # Update stats
        stats['total_requests'] += 1
        stats['total_tokens'] += tokens_generated
        stats['total_latency'] += latency

        return jsonify({
            'response': response['choices'][0]['text'].strip(),
            'model': MODEL_NAME,
            'latency_seconds': round(latency, 3),
            'tokens_generated': tokens_generated
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus-compatible metrics endpoint"""
    avg_latency = (stats['total_latency'] / stats['total_requests']
                   if stats['total_requests'] > 0 else 0)

    return jsonify({
        'total_requests': stats['total_requests'],
        'total_tokens': stats['total_tokens'],
        'average_latency_seconds': round(avg_latency, 3),
        'model': MODEL_NAME
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
