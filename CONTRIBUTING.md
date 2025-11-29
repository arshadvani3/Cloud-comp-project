# Contributing Guide

Thank you for your interest in this project! This is an educational project for cloud computing, and we welcome contributions.

## 🚀 Quick Setup for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/llm-inference-service.git
cd llm-inference-service
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Ollama (macOS/Linux)

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama (in separate terminal)
ollama serve

# Download CodeLlama
ollama pull codellama:7b-instruct
```

### 4. Test Locally

```bash
# Start the API
python src/app.py

# In another terminal, test it
curl http://localhost:8080/health
```

Open browser to `http://localhost:8080/` to see the frontend.

---

## 📝 Making Changes

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

### Testing

Before submitting changes:

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test code generation
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python hello world", "max_tokens": 100}'
```

### Commit Messages

Use clear, descriptive commit messages:

```
Good: "Add error handling for model loading timeout"
Bad: "fix bug"
```

---

## 🔧 Common Modifications

### Try Different Models

Edit `src/inference_ollama.py`:

```python
# Change from CodeLlama to another model
self.model_name = "llama3.2:3b"  # or any other Ollama model
```

Then:
```bash
ollama pull llama3.2:3b
python src/app.py
```

### Adjust Resource Limits

Edit `k8s/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "6Gi"  # Increase for larger models
    cpu: "3"
  limits:
    memory: "10Gi"
    cpu: "5"
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
        type: Utilization
        averageUtilization: 60  # Scale at 60% CPU
```

---

## 🧪 Running Tests

### Basic Load Test

```bash
# Update SERVICE_URL in tests/benchmark.py
SERVICE_URL = "http://localhost:8080"

# Run test
python tests/benchmark.py
```

### Advanced Tests

```bash
# Spike test
python tests/test_advanced.py --type spike --url http://localhost:8080

# Stress test
python tests/test_advanced.py --type stress --url http://localhost:8080

# Soak test (shorter for local testing)
python tests/test_advanced.py --type soak --url http://localhost:8080 --soak-duration 2
```

---

## 🐳 Testing with Docker

```bash
# Build image
docker build -t llm-inference:test .

# Run container
docker run -p 8080:8080 llm-inference:test

# Test it
curl http://localhost:8080/health
```

---

## 📊 Contribution Ideas

### Easy

- [ ] Add more example prompts to frontend
- [ ] Improve error messages
- [ ] Add input validation
- [ ] Update documentation

### Medium

- [ ] Add support for streaming responses
- [ ] Implement request caching
- [ ] Add Prometheus metrics export
- [ ] Create Grafana dashboards

### Advanced

- [ ] Add GPU support
- [ ] Implement model hot-swapping
- [ ] Add request batching
- [ ] Create custom HPA metrics

---

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Environment**:
   - OS (macOS, Linux, Windows)
   - Python version
   - Docker version (if applicable)
   - Kubernetes version (if applicable)

2. **Steps to Reproduce**:
   - Exact commands run
   - Expected behavior
   - Actual behavior

3. **Logs**:
   ```bash
   # API logs
   python src/app.py 2>&1 | tee app.log

   # Or Kubernetes logs
   kubectl logs <pod-name> -n llm-inference
   ```

4. **Configuration**:
   - Model being used
   - Any custom configuration

---

## 🎯 Pull Request Process

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code
   - Test locally
   - Update documentation

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Clear description of changes"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**:
   - Go to GitHub
   - Click "New Pull Request"
   - Describe your changes
   - Reference any related issues

---

## 💡 Questions?

- Check [README.md](README.md) for general documentation
- See [TESTING_EXECUTION_GUIDE.md](TESTING_EXECUTION_GUIDE.md) for testing details
- Review [PROJECT_STATUS.md](PROJECT_STATUS.md) for project status

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Happy contributing! 🎉**
