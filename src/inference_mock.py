"""Mock LLM inference for testing without llama-cpp-python"""
import time
import random

class LLMInference:
    """Mock LLM that simulates responses for testing"""

    def __init__(self, model_path, n_ctx=2048, n_threads=4):
        """Initialize the mock model"""
        print(f"Loading mock model from {model_path}...")
        start = time.time()
        time.sleep(0.5)  # Simulate loading time
        load_time = time.time() - start
        print(f"Mock model loaded in {load_time:.2f}s")
        print("⚠️  WARNING: Using mock LLM for testing!")
        print("   To use real LLM: pip install llama-cpp-python && download models")

    def generate(self, prompt, max_tokens=150, temperature=0.7):
        """Generate mock response"""
        # Simulate processing time
        time.sleep(random.uniform(0.3, 0.8))

        # Generate mock response based on prompt keywords
        responses = {
            "cloud": "Cloud computing is a technology that allows users to access computing resources over the internet. It provides on-demand access to servers, storage, databases, and applications without direct active management.",
            "kubernetes": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications across clusters of machines.",
            "docker": "Docker containers provide a lightweight, portable way to package applications and their dependencies. They ensure consistent behavior across different environments from development to production.",
            "default": "This is a mock response from the LLM inference service. The response is generated based on your prompt and simulates the behavior of a real language model for testing purposes."
        }

        # Select response based on prompt content
        response_text = responses["default"]
        prompt_lower = prompt.lower()
        for key in ["cloud", "kubernetes", "docker"]:
            if key in prompt_lower:
                response_text = responses[key]
                break

        # Simulate token count
        tokens = len(response_text.split())

        return {
            'choices': [{'text': response_text}],
            'usage': {
                'completion_tokens': tokens,
                'prompt_tokens': len(prompt.split()),
                'total_tokens': tokens + len(prompt.split())
            }
        }
