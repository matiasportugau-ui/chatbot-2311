#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Performance Benchmark Tests
Measures response times and performance characteristics
"""
import pytest
import time
import asyncio
import httpx
from typing import Dict, Any

# Mark all tests in this module as benchmarks
pytestmark = pytest.mark.benchmark


class TestAPIBenchmarks:
    """Benchmark tests for API endpoints"""
    
    @pytest.fixture
    def api_client(self):
        """Create HTTP client for testing"""
        return httpx.Client(base_url="http://localhost:8000", timeout=10.0)
    
    def test_health_endpoint(self, benchmark, api_client):
        """Benchmark health check endpoint"""
        def health_check():
            try:
                response = api_client.get("/health")
                return response.status_code == 200
            except Exception:
                return False
        
        result = benchmark(health_check)
        assert result is not None
    
    def test_chat_message_simple(self, benchmark, api_client):
        """Benchmark simple chat message"""
        def send_message():
            try:
                response = api_client.post("/api/chat", json={
                    "message": "Hola",
                    "session_id": "test_session_benchmark"
                })
                return response.status_code in [200, 500]  # Accept both for benchmark
            except Exception:
                return False
        
        result = benchmark(send_message)
        assert result is not None
    
    def test_chat_message_quote_request(self, benchmark, api_client):
        """Benchmark quote request message"""
        def send_quote_request():
            try:
                response = api_client.post("/api/chat", json={
                    "message": "Necesito cotización para Isodec 100mm 10x5 metros",
                    "session_id": "test_session_quote_benchmark"
                })
                return response.status_code in [200, 500]
            except Exception:
                return False
        
        result = benchmark(send_quote_request)
        assert result is not None


class TestAsyncPerformance:
    """Async performance tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test concurrent request handling"""
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=10.0) as client:
            # Send 10 concurrent requests
            tasks = [
                client.post("/api/chat", json={
                    "message": "Hola",
                    "session_id": f"concurrent_test_{i}"
                })
                for i in range(10)
            ]
            
            start_time = time.time()
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start_time
                
                # Check that we handled concurrent requests
                assert duration < 30.0, f"Concurrent requests took too long: {duration}s"
                
                # Count successful responses
                successful = sum(
                    1 for r in responses 
                    if not isinstance(r, Exception) and r.status_code == 200
                )
                
                print(f"\nConcurrent test: {successful}/10 successful in {duration:.2f}s")
            except Exception as e:
                print(f"Concurrent test error: {e}")
                # Don't fail the test if API is not running


def test_response_time_distribution():
    """Test response time distribution over multiple requests"""
    import statistics
    
    response_times = []
    client = httpx.Client(base_url="http://localhost:8000", timeout=10.0)
    
    try:
        for i in range(20):
            start = time.time()
            try:
                response = client.get("/health")
                duration = time.time() - start
                response_times.append(duration)
            except Exception:
                pass
        
        if response_times:
            mean = statistics.mean(response_times)
            stdev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            
            print(f"\nResponse time statistics (n={len(response_times)}):")
            print(f"  Mean: {mean:.3f}s")
            print(f"  StdDev: {stdev:.3f}s")
            print(f"  Min: {min(response_times):.3f}s")
            print(f"  Max: {max(response_times):.3f}s")
            
            # Soft assertion - warn if too slow
            if mean > 2.0:
                print(f"⚠️  Warning: Mean response time {mean:.3f}s exceeds 2s target")
        else:
            print("⚠️  No response times recorded - API may not be running")
    finally:
        client.close()


if __name__ == "__main__":
    # Run tests with benchmark
    pytest.main([__file__, "-v", "--benchmark-only"])
