"""Model loading and inference logic"""
from llama_cpp import Llama
import os
import time

class LLMInference:
    def __init__(self, model_path, n_ctx=2048, n_threads=4):
        """Initialize the LLM model"""
        print(f"Loading model from {model_path}...")
        start = time.time()

        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False
        )

        load_time = time.time() - start
        print(f"Model loaded in {load_time:.2f}s")

    def generate(self, prompt, max_tokens=150, temperature=0.7):
        """Generate response from prompt"""
        response = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "User:", "\n\n"]
        )
        return response
