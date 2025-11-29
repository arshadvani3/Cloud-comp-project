"""Ollama-based LLM inference for local development on macOS"""
import requests
import time

class LLMInference:
    """Ollama LLM inference adapter"""

    def __init__(self, model_path=None, n_ctx=2048, n_threads=4):
        """Initialize Ollama client"""
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3.2:3b"  # CodeLlama for code generation

        print(f"Initializing Ollama client...")
        print(f"Ollama URL: {self.ollama_url}")
        print(f"Model: {self.model_name}")

        start = time.time()

        # Check if Ollama is running
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=120)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                print(f"Available Ollama models: {model_names}")

                # Check if our model is available
                if not any(self.model_name in name for name in model_names):
                    print(f"⚠️  Warning: {self.model_name} not found in Ollama")
                    print(f"   Run: ollama pull {self.model_name}")
                else:
                    print(f"✅ Model {self.model_name} is available")
            else:
                print("⚠️  Warning: Could not connect to Ollama API")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: Ollama is not running!")
            print(f"   Start Ollama with: ollama serve")
            print(f"   Error details: {e}")
            raise ConnectionError("Ollama service is not running. Start with: ollama serve")

        load_time = time.time() - start
        print(f"Ollama client initialized in {load_time:.2f}s")

    def generate(self, prompt, max_tokens=150, temperature=0.7):
        """Generate response using Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=200
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')

                # Estimate token counts (Ollama doesn't always provide these)
                prompt_tokens = len(prompt.split())
                completion_tokens = len(response_text.split())

                # Format response to match llama-cpp-python structure
                return {
                    'choices': [{'text': response_text}],
                    'usage': {
                        'completion_tokens': completion_tokens,
                        'prompt_tokens': prompt_tokens,
                        'total_tokens': prompt_tokens + completion_tokens
                    }
                }
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
