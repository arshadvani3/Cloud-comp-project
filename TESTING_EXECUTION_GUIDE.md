# Complete Testing Execution Guide

## 🎯 Goal
Run comprehensive performance tests on your CodeLlama inference service, monitor auto-scaling behavior, and generate graphs for your final report.

**Your GCP External IP:** `http://34.70.42.27`

---

## 📋 Pre-Test Checklist

### 1. Verify Deployment is Running

```bash
# Set kubeconfig
export KUBECONFIG=~/nautilus-kubeconfig

# Check pods are running
kubectl get pods -n llm-inference

# Check HPA is configured
kubectl get hpa -n llm-inference

# Test API health
curl http://34.70.42.27/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "model": "codellama-7b-instruct-q4.gguf",
  "timestamp": "2025-11-26T..."
}
```

### 2. Verify Frontend Works

Open browser to: http://34.70.42.27/

Try generating code to ensure everything is connected properly.

---

## 🧪 Test Execution Plan

You'll run 4 types of tests in this order:

1. **Basic Load Test** - Warm up the system (5 minutes)
2. **Spike Test** - Test sudden traffic spikes (2 minutes)
3. **Stress Test** - Find breaking point (10-15 minutes)
4. **Soak Test** - Extended endurance test (10 minutes minimum)

---

## 🔥 Test 1: Basic Load Test (Warm Up)

### Purpose
- Warm up the service
- Establish baseline performance
- Verify auto-scaling triggers

### Setup Monitoring Windows

**Terminal 1 - Watch Pods Scaling:**
```bash
kubectl get pods -n llm-inference -w
```

**Terminal 2 - Watch HPA:**
```bash
kubectl get hpa -n llm-inference -w
```

**Terminal 3 - Run Test:**
```bash
cd /Users/arshadvani/Desktop/cloudprojext
python tests/benchmark.py
```

### What to Expect

**Test runs 3 scenarios:**
1. Light Load: 20 requests, 2 concurrent
2. Medium Load: 50 requests, 5 concurrent
3. Heavy Load: 100 requests, 10 concurrent

**Auto-scaling behavior:**
- Initial: 1 pod running
- After ~30 seconds of load: CPU > 70%, HPA triggers scaling
- Pods scale to 2-3 pods
- After test completes: Pods scale back down (takes 5 minutes)

### Expected Output

```
🔥 Load Test: 20 requests, 2 concurrent workers
======================================================================

📊 Results:
  Total Requests:     20
  Successful:         20 (100.0%)
  Failed:             0
  Total Time:         35.42s

⏱️  Latency Statistics:
  Average:            3.521s
  Median (P50):       3.445s
  P95:                4.123s
  P99:                4.456s
  Min:                2.234s
  Max:                4.567s

🚀 Throughput:
  Requests/sec:       0.56
  Tokens/sec:         28.45

✅ Results saved to benchmark_results.json
```

### Document for Report

**Take screenshots of:**
1. Terminal showing test results
2. HPA scaling output (kubectl get hpa)
3. Pods scaling from 1 → 2 → 3
4. Final benchmark_results.json

**Note down:**
- Average latency for each scenario
- Throughput (requests/sec)
- When auto-scaling triggered (timestamp)
- How many pods scaled to

---

## ⚡ Test 2: Spike Test

### Purpose
Test how the system handles sudden traffic bursts (simulates viral traffic).

### Run Test

```bash
python tests/test_advanced.py --type spike \
  --spike-baseline 2 \
  --spike-rps 15 \
  --spike-duration 30
```

### What This Does

**3 Phases:**
1. **Baseline** (30s): 2 req/sec - normal traffic
2. **SPIKE** (30s): 15 req/sec - sudden burst!
3. **Recovery** (30s): 2 req/sec - back to normal

### What to Monitor

In Terminal 1 & 2, watch for:
- Pods scaling up during spike phase
- CPU usage increasing
- Pods remaining scaled even after spike ends
- Gradual scale-down during recovery

### Expected Auto-Scaling Timeline

```
Time    | Phase     | RPS | Pods | CPU  | Notes
--------|-----------|-----|------|------|------------------
0:00    | Baseline  | 2   | 1    | 40%  | Starting
0:30    | SPIKE     | 15  | 1    | 85%  | Load hits!
0:50    | SPIKE     | 15  | 2    | 60%  | First scale-up
1:00    | SPIKE     | 15  | 3    | 50%  | Second scale-up
1:30    | Recovery  | 2   | 3    | 25%  | Spike over
6:30    | Recovery  | 2   | 1    | 40%  | Scale-down complete
```

### Document for Report

**Key metrics to capture:**
- Success rate during spike (should be 100%)
- Latency increase during spike
- Time to scale up (should be 30-60 seconds)
- Time to scale down (should be ~5 minutes)

**Screenshot:**
- HPA output showing pod count changes
- Test output showing 3 phase summaries

---

## 💪 Test 3: Stress Test (Find Breaking Point)

### Purpose
Incrementally increase load until system shows degradation.

### Run Test

```bash
python tests/test_advanced.py --type stress \
  --stress-start 1 \
  --stress-max 30 \
  --stress-step 3
```

### What This Does

**Incremental load increase:**
- Start: 1 req/sec for 60s
- Step 2: 4 req/sec for 60s
- Step 3: 7 req/sec for 60s
- ...continues until breaking point or max (30 req/sec)

**Breaking point criteria:**
- Success rate drops below 95%, OR
- Average latency exceeds 10 seconds

### What to Monitor

Watch for:
- Maximum pods scaled (should hit 5 with your HPA config)
- At what RPS does latency start increasing?
- At what RPS does success rate drop?

### Expected Breaking Point

**For CodeLlama 7B on CPU:**
- Comfortable throughput: 5-8 req/sec (across all pods)
- Breaking point: 20-30 req/sec
- Latency degradation starts: ~15 req/sec

### Document for Report

**Capture:**
```
RPS  | Pods | Success | Avg Latency | Status
-----|------|---------|-------------|--------
1    | 1    | 100%    | 3.2s        | ✅ Good
4    | 2    | 100%    | 3.5s        | ✅ Good
7    | 3    | 100%    | 3.8s        | ✅ Good
10   | 4    | 100%    | 4.2s        | ✅ Good
13   | 5    | 98%     | 5.8s        | ⚠️ Degrading
16   | 5    | 92%     | 8.4s        | ❌ Breaking
```

---

## ⏱️ Test 4: Soak Test (Endurance)

### Purpose
Test system stability under sustained load over extended period.

### Run Test

**Short version (10 minutes):**
```bash
python tests/test_advanced.py --type soak \
  --soak-rps 5 \
  --soak-duration 10
```

**Long version (if you have time - 30 minutes):**
```bash
python tests/test_advanced.py --type soak \
  --soak-rps 5 \
  --soak-duration 30
```

### What This Does

- Runs constant 5 req/sec for entire duration
- Monitors for degradation over time
- Checks for memory leaks
- Verifies system stability

### What to Monitor

**During test, watch for:**
- Pod memory usage (should be stable)
- Latency over time (should remain consistent)
- No pod restarts or OOMKills

```bash
# In another terminal - watch memory usage
kubectl top pods -n llm-inference
```

### Expected Behavior

**Healthy system:**
- Latency stays consistent (±10% variation)
- No pod crashes
- Memory usage stable or slight increase
- Success rate remains 100%

**Degradation signs (bad):**
- Latency increasing over time
- Memory constantly growing (leak!)
- Pods restarting
- Success rate dropping

### Document for Report

**Capture per-minute metrics:**
```
Minute | Avg Latency | P95 Latency | Success | Memory
-------|-------------|-------------|---------|--------
1      | 3.2s        | 4.1s        | 100%    | 6.2GB
2      | 3.3s        | 4.2s        | 100%    | 6.3GB
3      | 3.2s        | 4.0s        | 100%    | 6.3GB
...
10     | 3.4s        | 4.3s        | 100%    | 6.5GB
```

---

## 📊 Generate Graphs

After all tests complete, generate visualizations:

```bash
python scripts/analyze_results.py
```

### What Graphs Are Generated

1. **latency_comparison.png** - Compares latency across all test scenarios
2. **throughput_comparison.png** - Shows throughput for each scenario
3. **success_rate.png** - Success rates across scenarios

### Custom Graph for Advanced Tests

The advanced tests save results with timestamps. You can create custom graphs:

```python
# Example: Create spike test visualization
import json
import matplotlib.pyplot as plt

with open('advanced_test_results_YYYYMMDD_HHMMSS.json') as f:
    data = json.load(f)

spike = data['spike']
phases = ['baseline_results', 'spike_results', 'recovery_results']
latencies = [spike[p]['avg_latency'] for p in phases]

plt.bar(['Baseline', 'Spike', 'Recovery'], latencies)
plt.ylabel('Average Latency (s)')
plt.title('Spike Test - Latency Impact')
plt.savefig('spike_test_latency.png')
```

---

## 📈 Auto-Scaling Verification Checklist

### During Tests, Verify HPA is Working

```bash
# Watch HPA in real-time
kubectl get hpa -n llm-inference -w

# Check current metrics
kubectl describe hpa llm-inference -n llm-inference
```

**What you should see:**

```
NAME             REFERENCE                  TARGETS   MINPODS   MAXPODS   REPLICAS
llm-inference    Deployment/llm-inference   45%/70%   1         5         2
```

**TARGETS column explained:**
- `45%/70%` = Current CPU is 45%, threshold is 70%
- When current > 70%, HPA scales up
- When current < 70%, HPA scales down (after 5 min cooldown)

### Document Auto-Scaling Events

```bash
# View HPA scaling events
kubectl describe hpa llm-inference -n llm-inference | grep -A 10 Events
```

**Example events to capture:**
```
Events:
  Type    Reason             Message
  ----    ------             -------
  Normal  SuccessfulRescale  New size: 2; reason: cpu resource utilization (percentage of request) above target
  Normal  SuccessfulRescale  New size: 3; reason: cpu resource utilization (percentage of request) above target
  Normal  SuccessfulRescale  New size: 1; reason: All metrics below target
```

---

## 🎯 Complete Test Execution Timeline

**Total Time: ~45 minutes**

| Time      | Activity                          | Duration |
|-----------|-----------------------------------|----------|
| 0:00      | Setup monitoring terminals        | 5 min    |
| 0:05      | Run basic load test               | 5 min    |
| 0:10      | Wait for scale-down, document     | 5 min    |
| 0:15      | Run spike test                    | 2 min    |
| 0:17      | Wait for scale-down, document     | 5 min    |
| 0:22      | Run stress test                   | 10 min   |
| 0:32      | Wait for scale-down, document     | 5 min    |
| 0:37      | Run soak test (10 min version)    | 10 min   |
| 0:47      | Generate graphs                   | 3 min    |
| **0:50**  | **All testing complete!**         |          |

---

## 📝 Data Collection for Final Report

### Performance Metrics

**Basic Load Test:**
- [ ] Light load: latency, throughput
- [ ] Medium load: latency, throughput
- [ ] Heavy load: latency, throughput

**Spike Test:**
- [ ] Baseline phase metrics
- [ ] Spike phase metrics (latency increase %)
- [ ] Recovery phase metrics
- [ ] Time to recover

**Stress Test:**
- [ ] Breaking point (RPS)
- [ ] Maximum stable throughput
- [ ] Latency degradation curve

**Soak Test:**
- [ ] Latency stability over time
- [ ] Memory usage trend
- [ ] System stability (any crashes?)

### Auto-Scaling Metrics

- [ ] Time to scale up (baseline → spike)
- [ ] Time to scale down (spike → baseline)
- [ ] Maximum pods reached
- [ ] CPU utilization at each pod count
- [ ] HPA events timeline

### Screenshots to Take

1. [ ] kubectl get pods -n llm-inference (showing 1, 2, 3+ pods)
2. [ ] kubectl get hpa -n llm-inference (showing metrics)
3. [ ] Basic load test output
4. [ ] Spike test 3-phase summary
5. [ ] Stress test breaking point
6. [ ] Soak test per-minute analysis
7. [ ] All generated graphs
8. [ ] Frontend generating code

---

## 🚨 Troubleshooting

### Test Failing with Connection Errors

```bash
# Check service is accessible
curl http://34.70.42.27/health

# If not working, check service external IP
kubectl get svc -n llm-inference
```

### No Auto-Scaling Happening

```bash
# Check HPA exists
kubectl get hpa -n llm-inference

# Check metrics-server is working
kubectl top nodes
kubectl top pods -n llm-inference

# If "error: Metrics API not available", metrics-server might not be installed
```

### Pods Crashing During Heavy Load

```bash
# Check pod logs
kubectl logs <pod-name> -n llm-inference

# Check for OOMKilled
kubectl describe pod <pod-name> -n llm-inference

# If OOMKilled, increase memory limits in deployment.yaml
```

### Tests Timing Out

CodeLlama 7B on CPU is slow. If requests timeout:

1. Reduce RPS in tests
2. Increase timeout in test scripts (currently 60s)
3. Reduce max_tokens in prompts

---

## 🎓 For Your Presentation

### Demo Script

**1. Show the Service Running (2 min)**
```bash
kubectl get all -n llm-inference
curl http://34.70.42.27/health
```

**2. Show Frontend (1 min)**
- Open http://34.70.42.27/
- Generate code example live
- Show stats (latency, tokens, model)

**3. Demonstrate Auto-Scaling (5 min)**
```bash
# Terminal 1: Watch HPA
kubectl get hpa -n llm-inference -w

# Terminal 2: Run quick spike test
python tests/test_advanced.py --type spike --spike-duration 15

# Point out:
# - Initial 1 pod
# - Load hits, CPU rises
# - HPA triggers, pods scale to 2-3
# - Load stops, pods scale back down
```

**4. Show Performance Results (3 min)**
- Display graphs
- Explain breaking point
- Discuss throughput vs latency trade-offs

### Key Talking Points

✅ **Specialized for code generation** - CodeLlama 7B, not generic chat
✅ **Production deployment** - Kubernetes on GCP with auto-scaling
✅ **Comprehensive testing** - Load, spike, stress, soak
✅ **Auto-scaling validated** - HPA working, 1-5 pod range
✅ **Performance benchmarked** - X req/sec throughput, Y sec latency
✅ **Cost-effective** - Free Nautilus cluster + $X GCP spent
✅ **Modern web interface** - Real-time code generation UI

---

## ✅ Final Checklist Before Presentation

- [ ] All 4 test types executed
- [ ] benchmark_results.json exists
- [ ] advanced_test_results_*.json files exist
- [ ] All graphs generated (PNG files)
- [ ] Screenshots collected
- [ ] Auto-scaling events documented
- [ ] Breaking point identified
- [ ] Presentation slides updated with data
- [ ] Demo script practiced
- [ ] Frontend working smoothly

---

**Good luck with your testing and presentation! 🚀**

You now have a complete, production-grade LLM inference service with comprehensive performance data!
