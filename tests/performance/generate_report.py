#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate performance test report
Aggregates benchmark and load test results
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def load_benchmark_results() -> Dict[str, Any]:
    """Load pytest-benchmark results"""
    benchmark_file = Path("logs/performance/benchmark_results.json")
    
    if not benchmark_file.exists():
        return {}
    
    try:
        with open(benchmark_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading benchmark results: {e}")
        return {}


def load_locust_results() -> Dict[str, Any]:
    """Load Locust CSV results"""
    locust_stats_file = Path("logs/performance/locust_stats.csv")
    
    if not locust_stats_file.exists():
        return {}
    
    try:
        # Parse CSV and extract key metrics
        import csv
        with open(locust_stats_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if rows:
                # Get aggregate stats (usually last row)
                aggregate = rows[-1] if rows else {}
                return {
                    'total_requests': aggregate.get('Request Count', 'N/A'),
                    'failures': aggregate.get('Failure Count', 'N/A'),
                    'avg_response_time': aggregate.get('Average Response Time', 'N/A'),
                    'min_response_time': aggregate.get('Min Response Time', 'N/A'),
                    'max_response_time': aggregate.get('Max Response Time', 'N/A'),
                    'requests_per_second': aggregate.get('Requests/s', 'N/A'),
                }
    except Exception as e:
        print(f"Error loading Locust results: {e}")
        return {}


def generate_markdown_report(
    benchmark_data: Dict[str, Any],
    locust_data: Dict[str, Any]
) -> str:
    """Generate Markdown performance report"""
    
    report = f"""# 🚀 Performance Test Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Test Run:** Automated Performance Testing

---

## 📊 Executive Summary

"""
    
    # Add benchmark summary
    if benchmark_data and 'benchmarks' in benchmark_data:
        benchmarks = benchmark_data['benchmarks']
        report += f"""### API Benchmark Tests

**Total Tests:** {len(benchmarks)}

| Test Name | Mean Time | Min | Max | StdDev | Iterations |
|-----------|-----------|-----|-----|--------|------------|
"""
        for bench in benchmarks:
            stats = bench.get('stats', {})
            report += f"| {bench.get('name', 'Unknown')} | "
            report += f"{stats.get('mean', 0):.3f}s | "
            report += f"{stats.get('min', 0):.3f}s | "
            report += f"{stats.get('max', 0):.3f}s | "
            report += f"{stats.get('stddev', 0):.3f}s | "
            report += f"{stats.get('iterations', 0)} |\n"
        
        report += "\n"
    else:
        report += "_No benchmark data available_\n\n"
    
    # Add load test summary
    if locust_data:
        report += f"""### Load Test Results

| Metric | Value |
|--------|-------|
| **Total Requests** | {locust_data.get('total_requests', 'N/A')} |
| **Failed Requests** | {locust_data.get('failures', 'N/A')} |
| **Average Response Time** | {locust_data.get('avg_response_time', 'N/A')}ms |
| **Min Response Time** | {locust_data.get('min_response_time', 'N/A')}ms |
| **Max Response Time** | {locust_data.get('max_response_time', 'N/A')}ms |
| **Throughput** | {locust_data.get('requests_per_second', 'N/A')} req/s |

"""
    else:
        report += "_No load test data available_\n\n"
    
    # Add recommendations
    report += """---

## 🎯 Performance Analysis

### Key Findings

"""
    
    # Analyze benchmark data
    if benchmark_data and 'benchmarks' in benchmark_data:
        slow_tests = [
            b for b in benchmark_data['benchmarks']
            if b.get('stats', {}).get('mean', 0) > 2.0
        ]
        
        if slow_tests:
            report += "**⚠️ Slow API Endpoints Detected:**\n\n"
            for test in slow_tests:
                report += f"- `{test['name']}`: {test['stats']['mean']:.3f}s (target: <2.0s)\n"
            report += "\n"
        else:
            report += "✅ All API endpoints meet performance targets (<2s)\n\n"
    
    # Analyze load test data
    if locust_data:
        try:
            failures = int(locust_data.get('failures', '0'))
            total = int(locust_data.get('total_requests', '1'))
            failure_rate = (failures / total * 100) if total > 0 else 0
            
            if failure_rate > 5.0:
                report += f"**⚠️ High Failure Rate:** {failure_rate:.2f}% (target: <1%)\n\n"
            elif failure_rate > 0:
                report += f"**ℹ️ Minor Failures:** {failure_rate:.2f}% failure rate\n\n"
            else:
                report += "✅ Zero failures during load test\n\n"
        except (ValueError, ZeroDivisionError):
            pass
    
    report += """### Recommendations

1. **Monitor Response Times:** Continue tracking p95 and p99 response times
2. **Optimize Slow Endpoints:** Focus on endpoints exceeding 2s target
3. **Scale Testing:** Increase load gradually to find breaking point
4. **Caching:** Implement caching for frequently accessed data
5. **Database Optimization:** Review slow queries and add indexes

---

## 📈 Next Steps

- [ ] Review detailed logs for error patterns
- [ ] Implement recommended optimizations
- [ ] Re-run tests to measure improvements
- [ ] Set up continuous performance monitoring
- [ ] Configure alerts for performance degradation

---

**Report Location:** `logs/performance/performance_report.md`  
**Artifacts:** Available in GitHub Actions artifacts
"""
    
    return report


def main():
    """Generate performance report"""
    print("📊 Generating performance report...")
    
    # Load results
    benchmark_data = load_benchmark_results()
    locust_data = load_locust_results()
    
    # Generate report
    report = generate_markdown_report(benchmark_data, locust_data)
    
    # Save report
    output_file = Path("logs/performance/performance_report.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Report generated: {output_file}")
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
