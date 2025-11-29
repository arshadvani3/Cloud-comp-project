# Deployment Guide - CodeLlama v2

## 🚀 Quick Deploy to Kubernetes (Tomorrow)

### Prerequisites
- Docker Hub account: `arshadvani`
- Kubernetes namespace: `ucsc-cse239fall2025`
- Nautilus kubeconfig file

---

## Step 1: Test Locally with Ollama (Tonight)

### Install CodeLlama via Ollama

```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull CodeLlama
ollama pull codellama:7b-instruct
```

### Install flask-cors

```bash
cd /Users/arshadvani/Desktop/cloudprojext
source venv/bin/activate
pip install flask-cors
```

### Start the API

```bash
python src/app.py
```

Expected output:
```
🍎 Detected macOS - using Ollama for local development
Initializing Ollama client...
Model: codellama:7b-instruct
✅ Model codellama:7b-instruct is available
✅ Using Ollama inference engine
Service ready!
 * Running on http://0.0.0.0:8080
```

### Test the API

```bash
# Test health
curl http://localhost:8080/health

# Test code generation
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to reverse a string",
    "max_tokens": 500
  }'
```

### Test the Frontend

Open browser to: **http://localhost:8080/**

You should see the beautiful purple/blue gradient code generator interface!

Try the example buttons or type your own code request.

---

## Step 2: Build and Push Docker Image v2 (Tomorrow Morning)

### Build the image

```bash
cd /Users/arshadvani/Desktop/cloudprojext

# Build v2
docker build -t arshadvani/llm-inference:v2 .
```

### Test the Docker image locally (Optional)

```bash
# Run container
docker run -p 8080:8080 arshadvani/llm-inference:v2

# Note: This will download the CodeLlama model on first run (~4.5GB)
# Takes 5-10 minutes depending on connection

# Test it
curl http://localhost:8080/health
```

### Push to Docker Hub

```bash
# Login
docker login

# Push
docker push arshadvani/llm-inference:v2
```

---

## Step 3: Deploy to Kubernetes (Tomorrow)

### Configure kubectl

```bash
# Set kubeconfig
export KUBECONFIG=~/nautilus-kubeconfig

# Verify access
kubectl get nodes
kubectl get ns ucsc-cse239fall2025
```

### Deploy the application

```bash
cd /Users/arshadvani/Desktop/cloudprojext

# Apply all configs
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

### Monitor the deployment

```bash
# Watch pods starting
kubectl get pods -n ucsc-cse239fall2025 -w

# Check init container (model download)
kubectl logs <pod-name> -n ucsc-cse239fall2025 -c download-model

# Check main container
kubectl logs <pod-name> -n ucsc-cse239fall2025 -c llm-service
```

**Note:** The init container will download CodeLlama 7B (~4.5GB) which takes 5-10 minutes.

### Get the external IP

```bash
kubectl get svc llm-inference-service -n ucsc-cse239fall2025
```

Example output:
```
NAME                    TYPE           EXTERNAL-IP      PORT(S)        AGE
llm-inference-service   LoadBalancer   35.xxx.xxx.xxx   80:30123/TCP   5m
```

**Save this EXTERNAL-IP!** You'll need it for the frontend.

---

## Step 4: Update Frontend with External IP

### Option A: Edit the HTML file

Open `frontend/index.html` and find line 223:

```javascript
const API_URL = 'http://localhost:8080';
```

Change to:
```javascript
const API_URL = 'http://35.xxx.xxx.xxx';  // Your external IP
```

Then rebuild and push Docker image:
```bash
docker build -t arshadvani/llm-inference:v2 .
docker push arshadvani/llm-inference:v2

# Restart pods to get new version
kubectl rollout restart deployment llm-inference -n ucsc-cse239fall2025
```

### Option B: Deploy frontend separately (Recommended)

1. Create a new HTML file with the updated API_URL
2. Deploy to **Netlify** or **Vercel** (free hosting)

**For Netlify:**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend/
netlify deploy
# Follow prompts, select frontend/ as publish directory
```

**For Vercel:**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend/
vercel
```

---

## Step 5: Test the Deployment

### Test API directly

```bash
# Health check
curl http://YOUR-EXTERNAL-IP/health

# Code generation
curl -X POST http://YOUR-EXTERNAL-IP/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to check if a number is prime",
    "max_tokens": 500,
    "temperature": 0.3
  }'
```

### Test frontend

Open browser to:
- **If serving from Flask:** `http://YOUR-EXTERNAL-IP/`
- **If deployed separately:** Your Netlify/Vercel URL

Try these prompts:
1. "Write a Python function to reverse a string"
2. "Create a JavaScript function to validate email"
3. "Write a SQL query for top 5 customers by purchase amount"

---

## Step 6: Run Benchmarks

Update `tests/benchmark.py` line 96:

```python
SERVICE_URL = "http://YOUR-EXTERNAL-IP"
```

Then run:

```bash
# Basic load test
python tests/benchmark.py

# Advanced tests
python tests/test_advanced.py --type spike
python tests/test_advanced.py --type stress

# Analyze results
python scripts/analyze_results.py
```

---

## Expected Performance (CodeLlama 7B)

| Metric | Expected Value |
|--------|----------------|
| **Model Download Time** | 5-10 minutes (first pod start) |
| **Pod Startup Time** | 30-60 seconds (after model downloaded) |
| **Code Generation Latency** | 2-4 seconds (CPU) |
| **Throughput** | 20-30 req/s per pod |
| **Auto-scale Time** | 30-60 seconds |
| **Memory Usage** | 6-8GB per pod |

---

## Troubleshooting

### Issue: "Model not found" in Ollama

```bash
ollama pull codellama:7b-instruct
ollama list  # Verify it's there
```

### Issue: "CORS error" in frontend

Make sure flask-cors is installed:
```bash
pip install flask-cors
```

And CORS is enabled in app.py (it should be already).

### Issue: Init container failing

```bash
# Check logs
kubectl logs <pod-name> -n ucsc-cse239fall2025 -c download-model

# Common issue: wget timeout
# Solution: Wait and let it retry, or increase timeout in deployment.yaml
```

### Issue: Pod OOMKilled

```bash
# Check pod status
kubectl describe pod <pod-name> -n ucsc-cse239fall2025

# Solution: Increase memory limits in deployment.yaml (already set to 12Gi)
```

### Issue: Frontend can't connect to API

1. Check external IP is correct
2. Check CORS is enabled
3. Check pod is running: `kubectl get pods -n ucsc-cse239fall2025`
4. Check service: `kubectl get svc -n ucsc-cse239fall2025`

---

## For Your Presentation

### Demo Flow:

1. **Show the frontend** - Beautiful UI
2. **Enter a prompt** - "Write a Python function to find factorial"
3. **Click Generate** - Show loading spinner
4. **Show result** - Code appears in ~3 seconds
5. **Show stats** - Latency, tokens, model
6. **Try examples** - Click example buttons
7. **Show auto-scaling** - `kubectl get hpa`

### Key Talking Points:

- "Specialized AI model for code generation (CodeLlama 7B)"
- "Modern web interface with real-time code generation"
- "Deployed on Kubernetes with auto-scaling"
- "Handles 20-30 code generation requests per second"
- "Auto-scales from 1 to 5 pods based on demand"
- "Free deployment using Nautilus research cluster"

---

## Quick Command Reference

```bash
# LOCAL TESTING
ollama pull codellama:7b-instruct
python src/app.py
# Open http://localhost:8080

# BUILD & PUSH
docker build -t arshadvani/llm-inference:v2 .
docker push arshadvani/llm-inference:v2

# DEPLOY
export KUBECONFIG=~/nautilus-kubeconfig
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# MONITOR
kubectl get pods -n ucsc-cse239fall2025 -w
kubectl logs -f <pod-name> -n ucsc-cse239fall2025
kubectl get hpa -n ucsc-cse239fall2025

# TEST
curl http://YOUR-IP/health
python tests/benchmark.py
```

---

## Timeline for Tomorrow

**Morning (9 AM - 12 PM):**
1. Build Docker image v2 (30 min)
2. Push to Docker Hub (10 min)
3. Deploy to Kubernetes (10 min)
4. Wait for pod to start + download model (10-15 min)
5. Test deployment (15 min)
6. Update frontend with external IP (10 min)

**Afternoon (1 PM - 5 PM):**
1. Run all benchmarks (1 hour)
2. Analyze results (30 min)
3. Generate charts (30 min)
4. Test auto-scaling (30 min)
5. Take screenshots for presentation (30 min)
6. Practice demo (1 hour)

**Total: ~6 hours** - You'll be ready!

---

Good luck! 🚀 You've got a professional code generation service ready to deploy!
