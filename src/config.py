"""Configuration settings for the LLM service"""
import os

# Model Configuration
MODEL_PATH = os.environ.get('MODEL_PATH', 'models/llama-3.2-3b-q4.gguf')
MODEL_CONTEXT_SIZE = int(os.environ.get('MODEL_CONTEXT_SIZE', '2048'))
MODEL_THREADS = int(os.environ.get('MODEL_THREADS', '4'))

# API Configuration
API_HOST = os.environ.get('API_HOST', '0.0.0.0')
API_PORT = int(os.environ.get('API_PORT', '8080'))

# Default Generation Parameters
DEFAULT_MAX_TOKENS = int(os.environ.get('DEFAULT_MAX_TOKENS', '150'))
DEFAULT_TEMPERATURE = float(os.environ.get('DEFAULT_TEMPERATURE', '0.7'))

# Model configurations for different scenarios
MODEL_CONFIGS = {
    'llama-3.2-3b': {
        'filename': 'llama-3.2-3b-q4.gguf',
        'url': 'https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf',
        'size_gb': 2.0,
        'recommended_ram': '4GB',
        'recommended_threads': 4
    },
    'llama-3.1-8b': {
        'filename': 'llama-3.1-8b-q4.gguf',
        'url': 'https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF/resolve/main/Llama-3.1-8B-Instruct-Q4_K_M.gguf',
        'size_gb': 4.5,
        'recommended_ram': '8GB',
        'recommended_threads': 8
    }
}

def get_model_info(model_path):
    """Get information about the currently loaded model"""
    model_name = os.path.basename(model_path)

    for key, config in MODEL_CONFIGS.items():
        if config['filename'] in model_name:
            return {
                'name': key,
                'path': model_path,
                **config
            }

    return {
        'name': 'unknown',
        'path': model_path,
        'filename': model_name
    }
