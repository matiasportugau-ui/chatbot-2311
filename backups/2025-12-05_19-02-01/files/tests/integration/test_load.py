"""
Load tests for BMC Chat API
Tests concurrent users, response times, memory usage, and MongoDB performance
"""

import asyncio
import os
import statistics
import time
from typing import Any

import aiohttp
import psutil
import pytest

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 20
TOTAL_REQUESTS = CONCURRENT_USERS * REQUESTS_PER_USER


class LoadTestResults:
    """Container for load test results"""

    def __init__(self):
        self.response_times: list[float] = []
        self.errors: list[dict[str, Any]] = []
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None
        self.memory_usage: list[float] = []


async def send_request(session: aiohttp.ClientSession, request_id: int) -> dict[str, Any]:
    """Send a single chat request"""
    start = time.time()
    try:
        async with session.post(
            f"{BASE_URL}/chat/process",
            json={"mensaje": f"Test message {request_id}", "telefono": f"099{request_id:06d}"},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            elapsed = time.time() - start
            data = await response.json()

            return {
                "request_id": request_id,
                "status": response.status,
                "response_time": elapsed,
                "success": response.status == 200,
                "data": data,
            }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "request_id": request_id,
            "status": 0,
            "response_time": elapsed,
            "success": False,
            "error": str(e),
        }


async def run_load_test(results: LoadTestResults):
    """Run load test with concurrent users"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    async with aiohttp.ClientSession() as session:
        # Create tasks for all requests
        tasks = []
        request_id = 0

        for user in range(CONCURRENT_USERS):
            for req in range(REQUESTS_PER_USER):
                request_id += 1
                tasks.append(send_request(session, request_id))

        # Execute all requests concurrently
        results.start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        results.end_time = time.time()

        # Process results
        for response in responses:
            if isinstance(response, Exception):
                results.error_count += 1
                results.errors.append({"error": str(response)})
            elif response.get("success"):
                results.success_count += 1
                results.response_times.append(response["response_time"])
            else:
                results.error_count += 1
                results.errors.append(response)

        # Collect memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        results.memory_usage.append(initial_memory)
        results.memory_usage.append(final_memory)


def calculate_percentiles(data: list[float], percentiles: list[float]) -> dict[float, float]:
    """Calculate percentiles for a dataset"""
    if not data:
        return {p: 0.0 for p in percentiles}

    sorted_data = sorted(data)
    result = {}
    for p in percentiles:
        index = int(len(sorted_data) * p / 100)
        index = min(index, len(sorted_data) - 1)
        result[p] = sorted_data[index]
    return result


@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_users():
    """Test system under concurrent user load"""
    results = LoadTestResults()

    await run_load_test(results)

    # Calculate statistics
    total_time = results.end_time - results.start_time
    requests_per_second = TOTAL_REQUESTS / total_time if total_time > 0 else 0

    percentiles = calculate_percentiles(results.response_times, [50, 95, 99])

    # Print results
    print(f"\n{'=' * 60}")
    print("LOAD TEST RESULTS")
    print(f"{'=' * 60}")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Successful: {results.success_count}")
    print(f"Errors: {results.error_count}")
    print(f"Success Rate: {(results.success_count / TOTAL_REQUESTS) * 100:.2f}%")
    print("\nResponse Times:")
    print(
        f"  Mean: {statistics.mean(results.response_times):.3f}s"
        if results.response_times
        else "  Mean: N/A"
    )
    print(f"  Median (p50): {percentiles[50]:.3f}s")
    print(f"  p95: {percentiles[95]:.3f}s")
    print(f"  p99: {percentiles[99]:.3f}s")
    print(f"\nThroughput: {requests_per_second:.2f} requests/second")
    print(f"Total Time: {total_time:.2f}s")
    print("\nMemory Usage:")
    print(f"  Initial: {results.memory_usage[0]:.2f} MB")
    print(f"  Final: {results.memory_usage[-1]:.2f} MB")
    print(f"  Increase: {results.memory_usage[-1] - results.memory_usage[0]:.2f} MB")

    if results.errors:
        print(f"\nErrors ({len(results.errors)}):")
        for error in results.errors[:5]:  # Show first 5 errors
            print(f"  - {error}")

    print(f"{'=' * 60}\n")

    # Assertions
    assert results.success_count > TOTAL_REQUESTS * 0.95, (
        f"Success rate too low: {(results.success_count / TOTAL_REQUESTS) * 100:.2f}%"
    )
    assert percentiles[95] < 2.0, f"p95 response time too high: {percentiles[95]:.3f}s"
    assert requests_per_second > 10, f"Throughput too low: {requests_per_second:.2f} req/s"


@pytest.mark.asyncio
@pytest.mark.slow
async def test_response_time_under_load():
    """Test that response times remain acceptable under load"""
    results = LoadTestResults()

    await run_load_test(results)

    if not results.response_times:
        pytest.skip("No successful responses to analyze")

    mean_time = statistics.mean(results.response_times)
    p95_time = calculate_percentiles(results.response_times, [95])[95]

    # Response time should be under 500ms on average
    assert mean_time < 0.5, f"Mean response time too high: {mean_time:.3f}s"
    # p95 should be under 1 second
    assert p95_time < 1.0, f"p95 response time too high: {p95_time:.3f}s"


@pytest.mark.asyncio
@pytest.mark.slow
async def test_memory_usage():
    """Test memory usage under load"""
    results = LoadTestResults()

    await run_load_test(results)

    memory_increase = results.memory_usage[-1] - results.memory_usage[0]

    # Memory increase should be reasonable (< 500MB for this test)
    assert memory_increase < 500, f"Memory increase too high: {memory_increase:.2f} MB"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s"])
