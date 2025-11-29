# Setup Guide for Your Friend 👋

Hey! Welcome to the CodeLlama Inference Service project. This guide will help you get started quickly.

## What This Project Does

This is an AI code generation service that:
- Uses **CodeLlama 7B** (specialized AI for code)
- Has a beautiful web interface
- Runs on Kubernetes with auto-scaling
- Can handle 20-30 code generation requests per second
- Automatically scales from 1 to 5 pods based on load

**Live Demo**: http://34.70.42.27/

Try it out before setting up locally!

---

## 🚀 Quick Start (10 minutes)

### Option 1: macOS (Recommended for Local Testing)

```bash
# 1. Clone the repo
git clone <YOUR-REPO-URL>
cd llm-inference-service

# 2. Install Ollama (AI inference engine)
brew install ollama

# 3. Start Ollama (in a separate terminal, keep it running)
ollama serve

# 4. Download CodeLlama model (~4.5GB, takes 2-5 min)
ollama pull codellama:7b-instruct

# 5. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Start the service
python src/app.py
```

**Open browser**: http://localhost:8080/

You should see the purple/blue code generator interface!

### Option 2: Linux

```bash
# 1. Clone the repo
git clone <YOUR-REPO-URL>
cd llm-inference-service

# 2. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 3. Start Ollama (in separate terminal)
ollama serve

# 4. Download CodeLlama
ollama pull codellama:7b-instruct

# 5. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Start the service
python src/app.py
```

---

## 🧪 Try It Out

Once running locally, test the API:

```bash
# Test 1: Health check
curl http://localhost:8080/health

# Test 2: Generate code
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to reverse a string",
    "max_tokens": 500
  }'

# Test 3: Run load test
python tests/benchmark.py
```

Open the web interface at http://localhost:8080/ and try:
- "Write a Python function to check if a number is prime"
- "Create a JavaScript function to validate email"
- "Write a SQL query to find top 5 customers"

---

## 📁 Project Structure

```
llm-inference-service/
├── src/
│   ├── app.py                    # Main Flask API
│   ├── inference_ollama.py       # Uses Ollama (for local dev)
│   └── inference.py              # Uses llama-cpp-python (for production)
├── frontend/
│   └── index.html                # Web interface
├── k8s/
│   ├── deployment.yaml           # Kubernetes deployment config
│   ├── service.yaml              # LoadBalancer service
│   └── hpa.yaml                  # Auto-scaling rules
├── tests/
│   ├── benchmark.py              # Load testing
│   └── test_advanced.py          # Spike/stress/soak tests
└── README.md                     # Full documentation
```

---

## 🐳 Deploy to Kubernetes (Optional)

If you want to deploy this to your own Kubernetes cluster:

### Prerequisites
- Docker
- kubectl
- A Kubernetes cluster (GKE, EKS, local minikube)

### Steps

1. **Build Docker image**:
   ```bash
   docker build --platform linux/amd64 -t yourname/llm-inference:v1 .
   docker push yourname/llm-inference:v1
   ```

2. **Update deployment**:
   Edit `k8s/deployment.yaml` line 18:
   ```yaml
   image: yourname/llm-inference:v1  # Change this
   ```

3. **Deploy**:
   ```bash
   kubectl create namespace llm-inference
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/hpa.yaml
   ```

4. **Get external IP**:
   ```bash
   kubectl get svc llm-inference-service -n llm-inference
   ```

5. **Update frontend**:
   Edit `frontend/index.html` line 332 with your external IP, rebuild, and redeploy.

Full deployment guide: [DEPLOYMENT_GUIDE_V2.md](DEPLOYMENT_GUIDE_V2.md)

---

## 🧪 Run Tests

### Basic Load Test
```bash
# Edit tests/benchmark.py line 107 to set your URL
# Then run:
python tests/benchmark.py
```

This runs 3 scenarios:
- Light: 20 requests, 2 concurrent
- Medium: 50 requests, 5 concurrent
- Heavy: 100 requests, 10 concurrent

### Advanced Tests

**Spike Test** (sudden traffic burst):
```bash
python tests/test_advanced.py --type spike --url http://localhost:8080
```

**Stress Test** (find breaking point):
```bash
python tests/test_advanced.py --type stress --url http://localhost:8080
```

**Soak Test** (long-term stability):
```bash
python tests/test_advanced.py --type soak --url http://localhost:8080 --soak-duration 5
```

### Generate Graphs
```bash
python scripts/analyze_results.py
```

Creates:
- `latency_comparison.png`
- `throughput_comparison.png`
- `success_rate.png`

---

## 💡 What to Try

### Experiment with Different Models

Edit `src/inference_ollama.py` line 16:
```python
self.model_name = "llama3.2:3b"  # Smaller, faster model
# or
self.model_name = "codellama:13b-instruct"  # Larger, better quality
```

Then download it:
```bash
ollama pull llama3.2:3b
```

### Modify Auto-Scaling

Edit `k8s/hpa.yaml`:
```yaml
spec:
  minReplicas: 2        # Start with 2 pods
  maxReplicas: 10       # Scale up to 10 pods
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 60  # Scale at 60% CPU (was 70%)
```

### Try Different Prompts

The frontend has example buttons, but you can try:
- Code explanation: "Explain this code: [paste code]"
- Debugging: "Find the bug in: [paste code]"
- Conversion: "Convert this Python code to JavaScript: [paste code]"
- Optimization: "Optimize this function: [paste code]"

---

## 🐛 Troubleshooting

### "Connection refused" when accessing localhost:8080

- Make sure `python src/app.py` is running
- Check if Ollama is running: `ps aux | grep ollama`
- Try: `ollama serve` in a separate terminal

### "Model not found" error

```bash
# List installed models
ollama list

# If codellama not listed:
ollama pull codellama:7b-instruct
```

### Slow response times (>10 seconds)

This is normal for CodeLlama 7B on CPU. To speed up:
- Reduce `max_tokens` in your request (try 200 instead of 500)
- Use a smaller model: `ollama pull llama3.2:3b`
- Use GPU if available (requires different setup)

### Frontend shows but can't generate code

- Check API is running: `curl http://localhost:8080/health`
- Check browser console (F12) for errors
- Make sure `frontend/index.html` line 332 has correct URL

---

## 📚 Documentation

- **[README.md](README.md)** - Complete project documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current project status
- **[TESTING_EXECUTION_GUIDE.md](TESTING_EXECUTION_GUIDE.md)** - Detailed testing guide
- **[DEPLOYMENT_GUIDE_V2.md](DEPLOYMENT_GUIDE_V2.md)** - Kubernetes deployment

---

## 🤝 Questions?

1. Check the [Troubleshooting](#troubleshooting) section above
2. Read the full [README.md](README.md)
3. Look at existing code - it's well-commented!
4. Ask me (the original author) or create a GitHub issue

---

## 🎯 What Makes This Project Cool

1. **Real Production Deployment**: Not just a toy - this runs on real Kubernetes with auto-scaling
2. **Modern Tech Stack**: Latest AI model (CodeLlama 7B), beautiful UI, cloud-native architecture
3. **Comprehensive Testing**: Load, spike, stress, soak tests - not just basic testing
4. **Educational**: Great for learning Kubernetes, Docker, LLMs, and cloud computing
5. **Actually Useful**: Generate real code, not just demo responses

---

## 📊 Expected Performance

When you run load tests, you should see:

| Metric | Local (Ollama) | Kubernetes (Production) |
|--------|----------------|-------------------------|
| Latency | 2-4 seconds | 3-5 seconds |
| Throughput | 5-8 req/sec | 20-30 req/sec (with scaling) |
| Success Rate | 99-100% | 99-100% |

Auto-scaling behavior (on Kubernetes):
- Starts with 1 pod
- Scales to 2-3 pods under medium load
- Scales to 5 pods under heavy load
- Scales back down after 5 minutes

---

## ✅ Quick Checklist

Before running tests:
- [ ] Ollama is running (`ollama serve`)
- [ ] CodeLlama model downloaded (`ollama list`)
- [ ] API is running (`python src/app.py`)
- [ ] Health check works (`curl localhost:8080/health`)
- [ ] Frontend loads (open browser to localhost:8080)

You're ready to go! 🚀

---

**Have fun experimenting! Feel free to break things and learn.** 😊
