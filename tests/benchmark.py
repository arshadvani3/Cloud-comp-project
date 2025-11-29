"""Comprehensive benchmarking script"""
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class LoadTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []

    def send_request(self, prompt, max_tokens=100):
        """Send single request and measure latency"""
        start = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={'prompt': prompt, 'max_tokens': max_tokens},
                timeout=120  # Increased timeout for CodeLlama
            )
            latency = time.time() - start

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'latency': latency,
                    'server_latency': data.get('latency_seconds', 0),
                    'tokens': data.get('tokens_generated', 0)
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Request failed: {error_msg}")
                return {'success': False, 'latency': latency, 'error': error_msg}
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Request failed: {error_msg}")
            return {'success': False, 'latency': time.time() - start, 'error': error_msg}

    def run_load_test(self, num_requests, concurrency, prompt="Write a Python function to sort a list"):
        """Run load test with specified parameters"""
        print(f"\n{'='*70}")
        print(f"🔥 Load Test: {num_requests} requests, {concurrency} concurrent workers")
        print(f"{'='*70}")

        prompts = [prompt] * num_requests
        results = []

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.send_request, p, max_tokens=80) for p in prompts]

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                results.append(result)

                if i % 5 == 0 or i == num_requests:
                    print(f"  Progress: {i}/{num_requests} completed...")

        total_time = time.time() - start_time

        # Analyze results
        successful = [r for r in results if r['success']]
        failed = len(results) - len(successful)

        if successful:
            latencies = [r['latency'] for r in successful]
            tokens = [r['tokens'] for r in successful]

            print(f"\n📊 Results:")
            print(f"  Total Requests:     {num_requests}")
            print(f"  Successful:         {len(successful)} ({len(successful)/num_requests*100:.1f}%)")
            print(f"  Failed:             {failed}")
            print(f"  Total Time:         {total_time:.2f}s")
            print(f"\n⏱️  Latency Statistics:")
            print(f"  Average:            {statistics.mean(latencies):.3f}s")
            print(f"  Median (P50):       {statistics.median(latencies):.3f}s")
            
            if len(latencies) > 1:
                print(f"  P95:                {sorted(latencies)[int(len(latencies)*0.95)]:.3f}s")
                print(f"  P99:                {sorted(latencies)[max(0, int(len(latencies)*0.99)-1)]:.3f}s")
            
            print(f"  Min:                {min(latencies):.3f}s")
            print(f"  Max:                {max(latencies):.3f}s")
            print(f"\n🚀 Throughput:")
            print(f"  Requests/sec:       {len(successful) / total_time:.2f}")
            print(f"  Tokens/sec:         {sum(tokens) / total_time:.2f}")

            return {
                'total_requests': num_requests,
                'successful': len(successful),
                'failed': failed,
                'concurrency': concurrency,
                'total_time': total_time,
                'avg_latency': statistics.mean(latencies),
                'p50_latency': statistics.median(latencies),
                'min_latency': min(latencies),
                'max_latency': max(latencies),
                'throughput': len(successful) / total_time,
                'total_tokens': sum(tokens)
            }
        else:
            print("❌ All requests failed!")
            print("\n🔍 Sample errors:")
            for i, r in enumerate(results[:3]):
                if not r['success']:
                    print(f"  Error {i+1}: {r.get('error', 'Unknown')}")
            return None

def main():
    # Configure your service URL
    SERVICE_URL = "http://34.70.42.27"  # GCP External IP

    print(f"🎯 Testing CodeLlama 7B service at: {SERVICE_URL}")
    print(f"🔍 Testing health endpoint first...")
    
    # Test health endpoint first
    try:
        health = requests.get(f"{SERVICE_URL}/health", timeout=5)
        print(f"✅ Health check: {health.json()}\n")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("⚠️  Cannot proceed with tests. Fix the service first!")
        return

    tester = LoadTester(SERVICE_URL)

    # REDUCED test scenarios for CodeLlama stability
    scenarios = [
        {'requests': 5, 'concurrency': 1, 'name': 'Light Load (Sequential)'},
        {'requests': 10, 'concurrency': 2, 'name': 'Medium Load (2 Concurrent)'},
        {'requests': 15, 'concurrency': 3, 'name': 'Heavy Load (3 Concurrent)'},
    ]

    print("📋 Test Plan:")
    print("  - Light:  5 requests, 1 at a time  (~40-60 seconds)")
    print("  - Medium: 10 requests, 2 at a time (~60-90 seconds)")
    print("  - Heavy:  15 requests, 3 at a time (~80-120 seconds)")
    print("  - Total estimated time: ~5-8 minutes\n")

    all_results = []

    for scenario in scenarios:
        print(f"\n{'='*70}")
        print(f"🎯 Scenario: {scenario['name']}")
        print(f"{'='*70}")
        
        result = tester.run_load_test(scenario['requests'], scenario['concurrency'])
        
        if result:
            result['scenario'] = scenario['name']
            all_results.append(result)
            print(f"\n✅ {scenario['name']} completed successfully!")
        else:
            print(f"\n❌ {scenario['name']} failed!")
        
        # Wait between scenarios
        if scenario != scenarios[-1]:
            print("\n⏸️  Waiting 10 seconds before next scenario...")
            time.sleep(10)

    # Save results to file
    if all_results:
        with open('benchmark_results.json', 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✅ Results saved to benchmark_results.json")
        print(f"{'='*70}")
        
        # Print summary
        print(f"\n📈 Summary:")
        for result in all_results:
            print(f"\n  {result['scenario']}:")
            print(f"    Success Rate: {result['successful']}/{result['total_requests']} ({result['successful']/result['total_requests']*100:.1f}%)")
            print(f"    Avg Latency:  {result['avg_latency']:.2f}s")
            print(f"    Throughput:   {result['throughput']:.2f} req/s")
    else:
        print("\n❌ No successful test results to save.")

if __name__ == '__main__':
    main()