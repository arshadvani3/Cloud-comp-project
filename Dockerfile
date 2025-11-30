FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.11 python3-pip curl wget git && \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

WORKDIR /app

# Install prebuilt CUDA wheel
RUN pip install --no-cache-dir flask==3.0.0 flask-cors==4.0.0 \
    requests==2.31.0 numpy==1.26.0 prometheus-client==0.19.0 \
    gunicorn==21.2.0 && \
    pip install llama-cpp-python==0.2.90 \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118

COPY src/ ./src/
COPY frontend/ ./frontend/

RUN mkdir -p models && \
    wget https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf \
    -O models/codellama-7b-instruct-q4.gguf

EXPOSE 8080
CMD ["python", "src/app.py"]
