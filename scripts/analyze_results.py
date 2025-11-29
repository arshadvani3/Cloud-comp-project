"""Analyze benchmark results and generate charts"""
import json
import sys

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("⚠️  matplotlib and pandas not installed. Install with: pip install matplotlib pandas")

def load_results(filename='benchmark_results.json'):
    """Load benchmark results from file"""
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File {filename} not found!")
        print("Run benchmark.py first to generate results.")
        return None

def print_summary(results):
    """Print text summary of results"""
    print("\n" + "="*70)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("="*70 + "\n")

    for result in results:
        print(f"Scenario: {result['scenario']}")
        print(f"  Total Requests:    {result['total_requests']}")
        print(f"  Successful:        {result['successful']} ({result['successful']/result['total_requests']*100:.1f}%)")
        print(f"  Failed:            {result['failed']}")
        print(f"  Concurrency:       {result['concurrency']}")
        print(f"  Total Time:        {result['total_time']:.2f}s")
        print(f"  Avg Latency:       {result['avg_latency']:.3f}s")
        print(f"  P50 Latency:       {result['p50_latency']:.3f}s")
        print(f"  P95 Latency:       {result['p95_latency']:.3f}s")
        print(f"  P99 Latency:       {result['p99_latency']:.3f}s")
        print(f"  Throughput:        {result['throughput']:.2f} req/s")
        print()

def generate_charts(results):
    """Generate visualization charts"""
    if not HAS_PLOTTING:
        print("⚠️  Skipping chart generation (matplotlib not available)")
        return

    df = pd.DataFrame(results)

    # Chart 1: Latency Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(df))
    width = 0.25

    ax.bar([i - width for i in x], df['avg_latency'], width, label='Average', alpha=0.8)
    ax.bar(x, df['p95_latency'], width, label='P95', alpha=0.8)
    ax.bar([i + width for i in x], df['p99_latency'], width, label='P99', alpha=0.8)

    ax.set_ylabel('Latency (seconds)')
    ax.set_xlabel('Scenario')
    ax.set_title('Latency Comparison Across Load Scenarios')
    ax.set_xticks(x)
    ax.set_xticklabels(df['scenario'], rotation=15)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('latency_comparison.png', dpi=300)
    print("✅ Saved: latency_comparison.png")

    # Chart 2: Throughput
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df['scenario'], df['throughput'], alpha=0.8, color='steelblue')

    ax.set_ylabel('Throughput (requests/second)')
    ax.set_xlabel('Scenario')
    ax.set_title('Throughput Across Load Scenarios')
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')

    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig('throughput_comparison.png', dpi=300)
    print("✅ Saved: throughput_comparison.png")

    # Chart 3: Success Rate
    fig, ax = plt.subplots(figsize=(10, 6))
    success_rate = (df['successful'] / df['total_requests'] * 100)
    bars = ax.bar(df['scenario'], success_rate, alpha=0.8, color='green')

    ax.set_ylabel('Success Rate (%)')
    ax.set_xlabel('Scenario')
    ax.set_title('Request Success Rate')
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')

    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig('success_rate.png', dpi=300)
    print("✅ Saved: success_rate.png")

    plt.close('all')

def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else 'benchmark_results.json'

    results = load_results(filename)
    if not results:
        return

    print_summary(results)

    if HAS_PLOTTING:
        print("\n📈 Generating charts...")
        generate_charts(results)
        print("\n✅ Analysis complete!")
    else:
        print("\n💡 To generate charts, install: pip install matplotlib pandas")

if __name__ == '__main__':
    main()
