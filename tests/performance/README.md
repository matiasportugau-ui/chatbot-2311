# 🧪 Performance Testing Suite

## Overview

This directory contains the complete performance testing suite for the BMC Uruguay chatbot system. The tests are designed to measure API performance, simulate realistic load, and provide comprehensive benchmarking data.

## Test Files

### 1. `test_api_benchmarks.py`
**Purpose:** Measures API endpoint response times and performance characteristics

**Features:**
- Individual endpoint benchmarks
- Concurrent request testing
- Response time distribution analysis
- Graceful handling of API unavailability

**Usage:**
```bash
# Run all benchmarks
pytest test_api_benchmarks.py -v --benchmark-only

# Run with JSON output
pytest test_api_benchmarks.py -v --benchmark-only --benchmark-json=results.json

# Run only specific test
pytest test_api_benchmarks.py::TestAPIBenchmarks::test_health_endpoint -v --benchmark-only
```

**Test Coverage:**
- `/health` endpoint performance
- Simple chat messages
- Quote request messages
- Concurrent request handling (10 simultaneous users)
- Response time statistics

### 2. `locustfile.py`
**Purpose:** Load testing with realistic user behavior simulation

**Features:**
- Simulates different conversation types (greetings, product info, quotes, technical)
- Weighted task distribution (realistic user patterns)
- Complete quote flow simulation
- Detailed metrics collection
- Automated reporting

**Usage:**
```bash
# Web UI mode (with dashboard)
locust -f locustfile.py --host http://localhost:8000

# Headless mode (automated testing)
locust -f locustfile.py --headless -u 10 -r 2 -t 2m --host http://localhost:8000

# With HTML report
locust -f locustfile.py --headless -u 50 -r 5 -t 5m --host http://localhost:8000 \
  --html locust_report.html --csv locust_results

# High load test
locust -f locustfile.py --headless -u 100 -r 10 -t 10m --host http://localhost:8000
```

**Parameters:**
- `-u`: Number of concurrent users
- `-r`: Spawn rate (users per second)
- `-t`: Test duration
- `--host`: Target API URL

**User Classes:**
1. **ChatbotUser** (General interactions)
   - 30% greetings
   - 50% product inquiries
   - 20% quote requests
   - 10% technical questions

2. **QuoteFlowUser** (Complete flows)
   - Simulates full quote conversation
   - 5-step flow from greeting to contact info

### 3. `generate_report.py`
**Purpose:** Aggregates test results and generates comprehensive reports

**Features:**
- Combines pytest-benchmark and Locust results
- Markdown report generation
- Performance analysis
- Recommendations based on metrics

**Usage:**
```bash
# Generate report from existing test results
python generate_report.py

# Output: logs/performance/performance_report.md
```

**Report Includes:**
- Executive summary
- Benchmark test results table
- Load test metrics
- Key findings
- Performance recommendations
- Next steps

## CI/CD Integration

The performance tests are automatically run via GitHub Actions:

**Triggers:**
- Daily at 3 AM UTC (scheduled)
- Push to main branch
- Pull requests to main
- Manual workflow dispatch

**Workflow Steps:**
1. Setup Python environment
2. Install dependencies
3. Run benchmark tests
4. Start API server
5. Run load tests
6. Generate performance report
7. Upload artifacts
8. Comment on PR with results

**Artifacts Generated:**
- Benchmark results JSON
- Locust HTML report
- Locust CSV data
- Performance analysis report

## Local Testing

### Prerequisites
```bash
# Install testing dependencies
pip install -r requirements.txt
pip install locust pytest-benchmark pytest-asyncio httpx
```

### Quick Start
```bash
# 1. Start the API server
python api_server.py &

# 2. Wait for startup
sleep 5

# 3. Run benchmarks
pytest tests/performance/test_api_benchmarks.py -v --benchmark-only

# 4. Run load test
locust -f tests/performance/locustfile.py --headless -u 10 -r 2 -t 1m \
  --host http://localhost:8000

# 5. Generate report
python tests/performance/generate_report.py

# 6. View report
cat logs/performance/performance_report.md
```

### With Docker
```bash
# Build and start services
docker-compose up -d

# Run tests
docker-compose exec app pytest tests/performance/test_api_benchmarks.py -v

# Stop services
docker-compose down
```

## Performance Targets

### API Response Times
| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| p50 | <1s | <1.5s | >2s |
| p95 | <2s | <3s | >5s |
| p99 | <5s | <7s | >10s |

### Load Capacity
| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Concurrent Users | 100+ | 50-100 | <50 |
| Throughput | 100+ req/s | 50-100 | <50 |
| Error Rate | <0.1% | <1% | >5% |

### Resource Usage
| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Memory | <512MB | <1GB | >2GB |
| CPU | <50% | <80% | >90% |

## Interpreting Results

### Benchmark Tests
```json
{
  "name": "test_chat_message_simple",
  "stats": {
    "mean": 0.245,      // Average time
    "stddev": 0.032,    // Variation
    "min": 0.198,       // Best case
    "max": 0.312,       // Worst case
    "iterations": 100   // Sample size
  }
}
```

**What to look for:**
- Mean < 2s ✅
- Low stddev (consistent) ✅
- Max < 5s ✅

### Load Test Results
```
Total requests: 1000
Failed requests: 5
Failure rate: 0.50%
Average response time: 1.2s
95th percentile: 2.1s
Requests/second: 16.7
```

**What to look for:**
- Failure rate < 1% ✅
- Average response < 2s ✅
- Good throughput ✅

## Troubleshooting

### Test Failures

**"Connection refused"**
```bash
# API not running - start it first
python api_server.py &
sleep 5
```

**"Timeout"**
```bash
# Increase timeout in test
# Or check if API is overwhelmed
```

**"High error rate"**
```bash
# Check API logs
tail -f logs/api.log

# Reduce concurrent users
locust -u 5 -r 1  # Start with 5 users
```

### Performance Issues

**Slow response times:**
1. Check database performance
2. Review API logs for slow queries
3. Profile code execution
4. Consider caching implementation

**High memory usage:**
1. Check for memory leaks
2. Profile memory allocation
3. Implement connection pooling
4. Add memory limits

**Low throughput:**
1. Check CPU usage
2. Review concurrent request handling
3. Consider horizontal scaling
4. Optimize database queries

## Best Practices

### Running Tests
1. **Baseline First:** Always establish baseline metrics before changes
2. **Consistent Environment:** Use same conditions for comparable results
3. **Warm-up Period:** Let API warm up before measuring
4. **Multiple Runs:** Run tests multiple times for reliability
5. **Realistic Load:** Simulate actual user patterns

### Analyzing Results
1. **Trend Analysis:** Compare over time, not just single runs
2. **Percentiles:** Focus on p95/p99, not just averages
3. **Error Patterns:** Investigate all failures
4. **Resource Correlation:** Monitor CPU/memory during tests
5. **User Impact:** Translate metrics to user experience

### Continuous Improvement
1. **Set Targets:** Define clear performance goals
2. **Monitor Trends:** Track metrics over time
3. **Alert on Degradation:** Set up automated alerts
4. **Regular Reviews:** Review performance weekly
5. **Document Changes:** Track what impacts performance

## Advanced Usage

### Custom Test Scenarios
```python
# Create custom Locust user
from locust import HttpUser, task, between

class CustomUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def my_scenario(self):
        self.client.post("/api/custom", json={"data": "test"})
```

### Performance Profiling
```bash
# Profile specific test
pytest test_api_benchmarks.py::test_name --profile

# Generate profiling report
python -m cProfile -o profile.stats api_server.py
snakeviz profile.stats  # Visualize
```

### Stress Testing
```bash
# Gradually increase load
locust -f locustfile.py --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --host http://localhost:8000

# Monitor with metrics
curl http://localhost:8000/metrics | grep chatbot
```

## Contributing

When adding new tests:

1. Follow existing patterns
2. Include error handling
3. Add meaningful assertions
4. Document test purpose
5. Update this README

## Related Documentation

- [Benchmarking Roadmap](../BENCHMARKING_OPPORTUNITIES_AND_INNOVATION_ROADMAP.md)
- [Visual Summary](../BENCHMARKING_VISUAL_SUMMARY.md)
- [Quick Reference](../BENCHMARKING_ANALYSIS_SUMMARY.md)
- [Performance Workflow](../../.github/workflows/performance.yml)

## Support

For questions or issues:
- Review test logs in `logs/performance/`
- Check GitHub Actions workflow runs
- See main repository documentation

---

**Last Updated:** December 2024  
**Maintainer:** Development Team  
**Version:** 1.0
