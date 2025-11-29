# AI Code Generator - CodeLlama Inference Service

A production-ready AI code generation service powered by **CodeLlama 7B**, deployed on Kubernetes with auto-scaling. Features a beautiful web interface for real-time code generation and comprehensive performance testing.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-green.svg)
![Kubernetes](https://img.shields.io/badge/kubernetes-ready-green.svg)

## 🎯 Features

- **Specialized AI Model**: CodeLlama 7B Instruct for code generation
- **Beautiful Web UI**: Modern interface with real-time code generation
- **Auto-Scaling**: Automatically scales 1-5 pods based on load
- **Production Ready**: Deployed on GCP with LoadBalancer
- **Comprehensive Testing**: Load, spike, stress, and soak tests
- **Multi-Environment**: Works locally (Ollama) and in production (llama-cpp-python)

## 🚀 Live Demo

**Frontend**: http://34.70.42.27/

Try generating code like:
- "Write a Python function to reverse a string"
- "Create a JavaScript function to validate email"
- "Write a SQL query to find top 5 customers"

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Architecture](#architecture)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerization)
- kubectl (for Kubernetes deployment)
- Ollama (for local development on macOS)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/llm-inference-service.git
cd llm-inference-service
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Local Development (macOS)

```bash
# Install Ollama
brew install ollama

# Start Ollama service (in separate terminal)
ollama serve

# Download CodeLlama model
ollama pull codellama:7b-instruct

# Start the API
python src/app.py
```

Open browser to `http://localhost:8080/`

### 4. Local Development (Linux/Production)

```bash
# Download CodeLlama model (~4.5GB)
cd models/
wget https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf \
  -O codellama-7b-instruct-q4.gguf

# Start the API
python src/app.py
```

---

## 🔧 Local Development

### Project Structure

```
cloudprojext/
├── src/
│   ├── app.py                    # Flask API with CORS
│   ├── inference.py              # llama-cpp-python (production)
│   ├── inference_ollama.py       # Ollama adapter (local macOS)
│   └── inference_mock.py         # Mock for testing
├── frontend/
│   └── index.html                # Web interface
├── k8s/
│   ├── deployment.yaml           # Kubernetes deployment
│   ├── service.yaml              # LoadBalancer service
│   └── hpa.yaml                  # Auto-scaling config
├── tests/
│   ├── benchmark.py              # Basic load tests
│   └── test_advanced.py          # Spike/stress/soak tests
├── scripts/
│   └── analyze_results.py        # Graph generation
├── Dockerfile                    # Container definition
└── requirements.txt              # Python dependencies
```

### Environment Auto-Detection

The app automatically detects the environment:

- **macOS + Not in Docker**: Uses Ollama (`codellama:7b-instruct`)
- **Linux / Docker / Kubernetes**: Uses llama-cpp-python with GGUF model
- **Testing**: Can use mock inference

### Test Locally

```bash
# Terminal 1: Start API
python src/app.py

# Terminal 2: Test health endpoint
curl http://localhost:8080/health

# Terminal 3: Test code generation
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to check if a number is prime",
    "max_tokens": 500
  }'
```

---

## 🐳 Docker Deployment

### Build Image

```bash
# Build for linux/amd64 (for Kubernetes)
docker build --platform linux/amd64 -t yourusername/llm-inference:v1 .

# Push to Docker Hub
docker login
docker push yourusername/llm-inference:v1
```

### Test Docker Image Locally

```bash
docker run -p 8080:8080 yourusername/llm-inference:v1

# Note: First run downloads CodeLlama model (~4.5GB)
# Takes 5-10 minutes depending on connection
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (GKE, Nautilus, or local)
- kubectl configured
- Docker image pushed to registry

### Update Deployment

Edit `k8s/deployment.yaml`:

```yaml
containers:
- name: llm-service
  image: yourusername/llm-inference:v1  # Update this
```

### Deploy

```bash
# Create namespace
kubectl create namespace llm-inference

# Deploy all resources
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Monitor deployment
kubectl get pods -n llm-inference -w
```

### Get External IP

```bash
kubectl get svc llm-inference-service -n llm-inference

# Output shows EXTERNAL-IP (may take 1-2 minutes)
# Update frontend/index.html with this IP
```

### Monitor Auto-Scaling

```bash
# Watch HPA
kubectl get hpa -n llm-inference -w

# Watch pods scaling
kubectl get pods -n llm-inference -w

# View scaling events
kubectl describe hpa llm-inference -n llm-inference
```

---

## 📡 API Documentation

### Base URL

- **Local**: `http://localhost:8080`
- **Production**: `http://YOUR-EXTERNAL-IP`

### Endpoints

#### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "model": "codellama-7b-instruct-q4.gguf"
}
```

#### POST /chat

Generate code from natural language prompt.

**Request**:
```json
{
  "prompt": "Write a Python function to reverse a string",
  "max_tokens": 500,
  "temperature": 0.3
}
```

**Response**:
```json
{
  "response": "def reverse_string(s):\n    return s[::-1]",
  "model": "codellama:7b-instruct",
  "latency_seconds": 3.245,
  "tokens_generated": 87
}
```

#### GET /metrics

Service metrics.

**Response**:
```json
{
  "total_requests": 42,
  "total_tokens": 3456,
  "average_latency_seconds": 3.2,
  "model": "codellama:7b-instruct"
}
```

#### GET /

Serves the web interface.

---

## 🧪 Testing

### Basic Load Test

```bash
python tests/benchmark.py
```

Runs 3 scenarios:
- Light Load: 20 requests, 2 concurrent
- Medium Load: 50 requests, 5 concurrent
- Heavy Load: 100 requests, 10 concurrent

### Advanced Tests

#### Spike Test
Test sudden traffic bursts:
```bash
python tests/test_advanced.py --type spike --spike-rps 15
```

#### Stress Test
Find breaking point:
```bash
python tests/test_advanced.py --type stress --stress-max 30
```

#### Soak Test
Extended endurance test:
```bash
python tests/test_advanced.py --type soak --soak-duration 10
```

### Generate Performance Graphs

```bash
python scripts/analyze_results.py
```

Generates:
- `latency_comparison.png`
- `throughput_comparison.png`
- `success_rate.png`

### Monitor During Tests

```bash
# Terminal 1: Watch pods
kubectl get pods -n llm-inference -w

# Terminal 2: Watch HPA
kubectl get hpa -n llm-inference -w
```

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  LoadBalancer Service       │
│  (External IP)              │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Kubernetes Cluster                  │
│  ┌────────────────────────────────┐  │
│  │  HPA (Auto-Scaling)            │  │
│  │  Min: 1, Max: 5 pods           │  │
│  │  Trigger: 70% CPU              │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌─────────┐  ┌─────────┐           │
│  │ Pod 1   │  │ Pod 2   │  ...      │
│  │         │  │         │           │
│  │ Flask   │  │ Flask   │           │
│  │ +       │  │ +       │           │
│  │ llama   │  │ llama   │           │
│  │ -cpp    │  │ -cpp    │           │
│  └─────────┘  └─────────┘           │
└──────────────────────────────────────┘
```

### Resource Requirements

**Per Pod**:
- CPU: 2 cores (request), 4 cores (limit)
- Memory: 4GB (request), 8GB (limit)
- Storage: ~5GB (model in emptyDir volume)

**Auto-Scaling**:
- Min Pods: 1
- Max Pods: 5
- CPU Threshold: 70%
- Scale-up time: ~30-60 seconds
- Scale-down cooldown: ~5 minutes

### Model Details

- **Name**: CodeLlama 7B Instruct
- **Format**: GGUF (4-bit quantized, Q4_K_M)
- **Size**: ~4.5GB
- **Context**: 4096 tokens
- **Specialization**: Code generation, debugging, explanation

---

## 📊 Performance

### Expected Metrics (CPU-only)

| Metric | Value |
|--------|-------|
| **Latency** | 3-4 seconds (average) |
| **Throughput** | 5-8 req/sec (all pods) |
| **Success Rate** | 99-100% |
| **Tokens/sec** | 20-30 per pod |
| **Breaking Point** | ~20-30 req/sec |

### Auto-Scaling Behavior

1. **Idle**: 1 pod running
2. **Load increases**: CPU > 70%
3. **Scale-up**: New pod starts (~30-60s)
4. **Load handled**: Distributed across pods
5. **Load decreases**: CPU < 70%
6. **Scale-down**: Excess pods terminated (~5 min)

---

## 🔧 Configuration

### Update Frontend URL

After deployment, update `frontend/index.html`:

```javascript
// Line 332
const API_URL = 'http://YOUR-EXTERNAL-IP';
```

Rebuild and redeploy Docker image.

### Adjust Resource Limits

Edit `k8s/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "4Gi"    # Increase for larger models
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
```

### Tune Auto-Scaling

Edit `k8s/hpa.yaml`:

```yaml
spec:
  minReplicas: 1        # Minimum pods
  maxReplicas: 5        # Maximum pods
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # CPU threshold
```

---

## 🐛 Troubleshooting

### Pod Stuck in Init

**Issue**: Init container downloading model

**Solution**: Wait 5-10 minutes for model download (~4.5GB)

**Check logs**:
```bash
kubectl logs <pod-name> -n llm-inference -c download-model
```

### Pod OOMKilled

**Issue**: Out of memory

**Solution**: Increase memory limits in `k8s/deployment.yaml`

```yaml
limits:
  memory: "12Gi"  # Increase from 8Gi
```

### External IP Pending

**Issue**: LoadBalancer not assigning IP

**Solution**: Check cloud provider supports LoadBalancer, or use NodePort/port-forward

```bash
kubectl port-forward svc/llm-inference-service 8080:80 -n llm-inference
```

### Frontend Can't Connect

1. Check external IP is correct
2. Verify CORS is enabled in `src/app.py`
3. Check pod is running: `kubectl get pods -n llm-inference`
4. Test API directly: `curl http://YOUR-IP/health`

---

## 📚 Additional Documentation

- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Complete project status and configuration
- [TESTING_EXECUTION_GUIDE.md](TESTING_EXECUTION_GUIDE.md) - Comprehensive testing guide
- [DEPLOYMENT_GUIDE_V2.md](DEPLOYMENT_GUIDE_V2.md) - Detailed deployment instructions

---

## 🤝 Contributing

This is an educational project for cloud computing coursework. Feel free to:

1. Fork the repository
2. Try different models (7B, 13B, etc.)
3. Experiment with auto-scaling parameters
4. Add monitoring (Prometheus, Grafana)
5. Share your results!

---

## 📄 License

MIT License - Free for educational and personal use.

---

## 🙏 Acknowledgments

- [CodeLlama](https://ai.meta.com/blog/code-llama-large-language-model-coding/) by Meta
- [llama.cpp](https://github.com/ggerganov/llama.cpp) for efficient inference
- [Ollama](https://ollama.ai/) for local development
- [TheBloke](https://huggingface.co/TheBloke) for GGUF model conversions
- Nautilus for free Kubernetes access
- UCSC CSE239 Cloud Computing course

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing GitHub Issues
3. Create a new issue with logs and configuration

---

**Built with ❤️ for cloud computing education**
