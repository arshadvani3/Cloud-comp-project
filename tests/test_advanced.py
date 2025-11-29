"""Advanced load testing: Spike, Stress, and Soak testing"""
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import argparse
from datetime import datetime

class AdvancedLoadTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []

    def send_request(self, prompt="Explain cloud computing", max_tokens=100):
        """Send single request and measure latency"""
        start = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={'prompt': prompt, 'max_tokens': max_tokens},
                timeout=60
            )
            latency = time.time() - start

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'latency': latency,
                    'tokens': data.get('tokens_generated', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'latency': latency,
                    'error': response.text,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'success': False,
                'latency': time.time() - start,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def spike_test(self, baseline_rps=2, spike_rps=20, spike_duration=30):
        """
        Spike Test: Sudden increase in load

        Args:
            baseline_rps: Requests per second during baseline (default: 2)
            spike_rps: Requests per second during spike (default: 20)
            spike_duration: Duration of spike in seconds (default: 30)
        """
        print(f"\n{'='*70}")
        print(f"🔥 SPIKE TEST")
        print(f"{'='*70}")
        print(f"Baseline: {baseline_rps} req/s for 30s")
        print(f"Spike: {spike_rps} req/s for {spike_duration}s")
        print(f"Recovery: {baseline_rps} req/s for 30s")
        print(f"{'='*70}\n")

        all_results = []

        # Phase 1: Baseline (30 seconds)
        print("📊 Phase 1: Baseline load (30s)...")
        baseline_results = self._run_sustained_load(baseline_rps, 30, "Baseline")
        all_results.extend(baseline_results)

        # Phase 2: Spike (spike_duration seconds)
        print(f"\n⚡ Phase 2: SPIKE! {spike_rps} req/s ({spike_duration}s)...")
        spike_results = self._run_sustained_load(spike_rps, spike_duration, "Spike")
        all_results.extend(spike_results)

        # Phase 3: Recovery (30 seconds)
        print("\n🔄 Phase 3: Recovery to baseline (30s)...")
        recovery_results = self._run_sustained_load(baseline_rps, 30, "Recovery")
        all_results.extend(recovery_results)

        self._print_phase_summary(baseline_results, "Baseline")
        self._print_phase_summary(spike_results, "Spike")
        self._print_phase_summary(recovery_results, "Recovery")

        return {
            'test_type': 'spike',
            'baseline_results': self._analyze_results(baseline_results),
            'spike_results': self._analyze_results(spike_results),
            'recovery_results': self._analyze_results(recovery_results),
            'all_results': all_results
        }

    def stress_test(self, start_rps=1, max_rps=50, step=5, step_duration=60):
        """
        Stress Test: Incrementally increase load until system breaks

        Args:
            start_rps: Starting requests per second (default: 1)
            max_rps: Maximum requests per second (default: 50)
            step: Increase by this many req/s each step (default: 5)
            step_duration: Duration of each step in seconds (default: 60)
        """
        print(f"\n{'='*70}")
        print(f"💪 STRESS TEST")
        print(f"{'='*70}")
        print(f"Start: {start_rps} req/s")
        print(f"Max: {max_rps} req/s")
        print(f"Step: +{step} req/s every {step_duration}s")
        print(f"{'='*70}\n")

        all_results = []
        breaking_point = None

        current_rps = start_rps
        while current_rps <= max_rps:
            print(f"\n📈 Testing {current_rps} req/s for {step_duration}s...")

            step_results = self._run_sustained_load(current_rps, step_duration, f"{current_rps}RPS")
            all_results.extend(step_results)

            # Analyze this step
            analysis = self._analyze_results(step_results)
            success_rate = analysis['success_rate']
            avg_latency = analysis['avg_latency']

            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Avg latency: {avg_latency:.3f}s")

            # Check if system is breaking (success rate < 95% or latency > 10s)
            if success_rate < 95 or avg_latency > 10:
                breaking_point = current_rps
                print(f"\n⚠️  BREAKING POINT REACHED at {current_rps} req/s!")
                print(f"  Success rate dropped to {success_rate:.1f}%")
                print(f"  Avg latency: {avg_latency:.3f}s")
                break

            current_rps += step

        if breaking_point is None:
            print(f"\n✅ System handled max load of {max_rps} req/s successfully!")

        return {
            'test_type': 'stress',
            'breaking_point': breaking_point,
            'max_tested': current_rps - step if breaking_point else max_rps,
            'all_results': all_results
        }

    def soak_test(self, target_rps=5, duration_minutes=10):
        """
        Soak Test: Sustained load over extended period

        Args:
            target_rps: Target requests per second (default: 5)
            duration_minutes: Test duration in minutes (default: 10)
        """
        duration_seconds = duration_minutes * 60

        print(f"\n{'='*70}")
        print(f"⏱️  SOAK TEST (ENDURANCE)")
        print(f"{'='*70}")
        print(f"Load: {target_rps} req/s")
        print(f"Duration: {duration_minutes} minutes ({duration_seconds}s)")
        print(f"Total requests: ~{target_rps * duration_seconds}")
        print(f"{'='*70}\n")
        print("This will take a while... Monitor for memory leaks and degradation.")
        print("Press Ctrl+C to stop early.\n")

        try:
            results = self._run_sustained_load(
                target_rps,
                duration_seconds,
                "Soak",
                show_progress_every=30  # Show progress every 30s
            )

            # Analyze results in chunks to detect degradation
            chunk_size = 60  # Analyze every 60 seconds
            chunks = [results[i:i+chunk_size*target_rps]
                     for i in range(0, len(results), chunk_size*target_rps)]

            print(f"\n📊 Degradation Analysis (per minute):")
            print(f"{'Minute':<10} {'Avg Latency':<15} {'P95 Latency':<15} {'Success Rate':<15}")
            print("-" * 60)

            for i, chunk in enumerate(chunks):
                if not chunk:
                    continue
                analysis = self._analyze_results(chunk)
                print(f"{i+1:<10} {analysis['avg_latency']:<15.3f} "
                      f"{analysis.get('p95_latency', 0):<15.3f} "
                      f"{analysis['success_rate']:<15.1f}%")

            overall_analysis = self._analyze_results(results)

            return {
                'test_type': 'soak',
                'duration_minutes': duration_minutes,
                'target_rps': target_rps,
                'overall_analysis': overall_analysis,
                'per_minute_chunks': [self._analyze_results(c) for c in chunks if c],
                'all_results': results
            }

        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user!")
            return {'test_type': 'soak', 'status': 'interrupted'}

    def _run_sustained_load(self, rps, duration_seconds, phase_name, show_progress_every=10):
        """Run sustained load at specified RPS for duration"""
        total_requests = int(rps * duration_seconds)
        interval = 1.0 / rps  # Time between requests

        results = []
        start_time = time.time()
        last_progress_time = start_time

        with ThreadPoolExecutor(max_workers=min(rps * 2, 50)) as executor:
            futures = []

            for i in range(total_requests):
                # Schedule request at specific time to maintain RPS
                target_time = start_time + (i * interval)
                sleep_time = target_time - time.time()

                if sleep_time > 0:
                    time.sleep(sleep_time)

                future = executor.submit(self.send_request)
                futures.append(future)

                # Show progress
                elapsed = time.time() - start_time
                if elapsed - (last_progress_time - start_time) >= show_progress_every:
                    progress = (i + 1) / total_requests * 100
                    print(f"  [{phase_name}] Progress: {i+1}/{total_requests} "
                          f"({progress:.1f}%) - Elapsed: {elapsed:.1f}s")
                    last_progress_time = time.time()

            # Collect all results
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        return results

    def _analyze_results(self, results):
        """Analyze a set of results"""
        if not results:
            return {}

        successful = [r for r in results if r['success']]
        failed = len(results) - len(successful)

        if not successful:
            return {
                'total': len(results),
                'successful': 0,
                'failed': failed,
                'success_rate': 0
            }

        latencies = [r['latency'] for r in successful]
        tokens = [r['tokens'] for r in successful]

        return {
            'total': len(results),
            'successful': len(successful),
            'failed': failed,
            'success_rate': len(successful) / len(results) * 100,
            'avg_latency': statistics.mean(latencies),
            'median_latency': statistics.median(latencies),
            'p95_latency': sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max(latencies),
            'p99_latency': sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 100 else max(latencies),
            'min_latency': min(latencies),
            'max_latency': max(latencies),
            'total_tokens': sum(tokens)
        }

    def _print_phase_summary(self, results, phase_name):
        """Print summary for a test phase"""
        analysis = self._analyze_results(results)

        print(f"\n📊 {phase_name} Phase Summary:")
        print(f"  Total Requests: {analysis['total']}")
        print(f"  Successful: {analysis['successful']} ({analysis['success_rate']:.1f}%)")
        print(f"  Failed: {analysis['failed']}")
        print(f"  Avg Latency: {analysis['avg_latency']:.3f}s")
        print(f"  P95 Latency: {analysis['p95_latency']:.3f}s")

def main():
    parser = argparse.ArgumentParser(description='Advanced Load Testing Suite')
    parser.add_argument('--url', default='http://34.70.42.27',
                       help='Base URL of the service (default: http://34.70.42.27)')
    parser.add_argument('--type', choices=['spike', 'stress', 'soak', 'all'],
                       required=True,
                       help='Type of test to run')

    # Spike test arguments
    parser.add_argument('--spike-baseline', type=int, default=2,
                       help='Baseline RPS for spike test (default: 2)')
    parser.add_argument('--spike-rps', type=int, default=20,
                       help='Peak RPS during spike (default: 20)')
    parser.add_argument('--spike-duration', type=int, default=30,
                       help='Spike duration in seconds (default: 30)')

    # Stress test arguments
    parser.add_argument('--stress-start', type=int, default=1,
                       help='Starting RPS for stress test (default: 1)')
    parser.add_argument('--stress-max', type=int, default=50,
                       help='Maximum RPS for stress test (default: 50)')
    parser.add_argument('--stress-step', type=int, default=5,
                       help='RPS increment for stress test (default: 5)')

    # Soak test arguments
    parser.add_argument('--soak-rps', type=int, default=5,
                       help='Target RPS for soak test (default: 5)')
    parser.add_argument('--soak-duration', type=int, default=10,
                       help='Soak test duration in minutes (default: 10)')

    args = parser.parse_args()

    tester = AdvancedLoadTester(args.url)
    all_results = {}

    print(f"\n🚀 Starting Advanced Load Tests against {args.url}")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        if args.type in ['spike', 'all']:
            result = tester.spike_test(
                baseline_rps=args.spike_baseline,
                spike_rps=args.spike_rps,
                spike_duration=args.spike_duration
            )
            all_results['spike'] = result

        if args.type in ['stress', 'all']:
            result = tester.stress_test(
                start_rps=args.stress_start,
                max_rps=args.stress_max,
                step=args.stress_step
            )
            all_results['stress'] = result

        if args.type in ['soak', 'all']:
            result = tester.soak_test(
                target_rps=args.soak_rps,
                duration_minutes=args.soak_duration
            )
            all_results['soak'] = result

        # Save results
        filename = f'advanced_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            # Remove detailed results to keep file size reasonable
            summary = {k: {**v, 'all_results': []} if 'all_results' in v else v
                      for k, v in all_results.items()}
            json.dump(summary, f, indent=2)

        print(f"\n✅ Results saved to {filename}")
        print(f"⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user!")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == '__main__':
    main()
