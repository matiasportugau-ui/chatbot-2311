"""
Load tests for concurrent users
"""

import asyncio
import os
import time

import pytest

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not available")
class TestConcurrentUsers:
    BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    CONCURRENT_USERS = 10
    REQUESTS_PER_USER = 5

    async def send_request(self, session, user_id, request_num):
        start_time = time.time()
        try:
            payload = {"mensaje": f"Test message {user_id}", "telefono": f"+598{user_id:08d}"}
            async with session.post(
                f"{self.BASE_URL}/chat/process",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response_time = time.time() - start_time
                return {"success": response.status == 200, "response_time": response_time}
        except Exception as e:
            return {"success": False, "response_time": time.time() - start_time, "error": str(e)}

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_users(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.send_request(session, user_id, req_num)
                for user_id in range(self.CONCURRENT_USERS)
                for req_num in range(self.REQUESTS_PER_USER)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = [r for r in results if isinstance(r, dict) and r.get("success")]
            response_times = [r["response_time"] for r in successful if "response_time" in r]
            success_rate = len(successful) / len(results) if results else 0
            assert success_rate > 0.8, f"Success rate too low: {success_rate * 100:.2f}%"
