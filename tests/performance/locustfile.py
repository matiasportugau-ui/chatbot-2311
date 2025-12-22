#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Locust Load Testing for BMC Chatbot API
Simulates realistic user conversation patterns
"""
from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime

# Test messages representing different conversation types
TEST_MESSAGES = {
    'greetings': [
        "Hola",
        "Buenos días",
        "Buenas tardes",
        "Hola, ¿cómo están?"
    ],
    'product_info': [
        "¿Qué productos tienen disponibles?",
        "Información sobre Isodec",
        "¿Qué es el poliestireno expandido?",
        "Cuéntame sobre la lana de roca"
    ],
    'quote_requests': [
        "Necesito una cotización",
        "Quiero cotizar Isodec 100mm 10x5 metros",
        "Cotización para panel de 150mm",
        "Precio de poliestireno 50mm"
    ],
    'technical': [
        "¿Cuál es la conductividad térmica del Isodec?",
        "Especificaciones técnicas del panel de 100mm",
        "¿Qué espesor me recomiendan?"
    ]
}


class ChatbotUser(HttpUser):
    """Simulates a user interacting with the chatbot"""
    
    wait_time = between(2, 5)  # Wait 2-5 seconds between requests
    
    def on_start(self):
        """Initialize user session"""
        self.session_id = f"load_test_{self.environment.runner.user_count}_{random.randint(1000, 9999)}"
        self.conversation_step = 0
    
    @task(3)
    def send_greeting(self):
        """Send greeting message (30% of requests)"""
        message = random.choice(TEST_MESSAGES['greetings'])
        self._send_chat_message(message, "greeting")
    
    @task(5)
    def ask_product_info(self):
        """Ask about products (50% of requests)"""
        message = random.choice(TEST_MESSAGES['product_info'])
        self._send_chat_message(message, "product_info")
    
    @task(2)
    def request_quote(self):
        """Request a quote (20% of requests)"""
        message = random.choice(TEST_MESSAGES['quote_requests'])
        self._send_chat_message(message, "quote_request")
    
    @task(1)
    def ask_technical(self):
        """Ask technical question (10% of requests)"""
        message = random.choice(TEST_MESSAGES['technical'])
        self._send_chat_message(message, "technical")
    
    def _send_chat_message(self, message: str, message_type: str):
        """Send chat message and track metrics"""
        self.conversation_step += 1
        
        with self.client.post(
            "/api/chat",
            json={
                "message": message,
                "session_id": self.session_id,
                "user_id": f"load_test_user_{self.environment.runner.user_count}"
            },
            catch_response=True,
            name=f"/api/chat/{message_type}"
        ) as response:
            try:
                if response.status_code == 200:
                    data = response.json()
                    # Validate response has expected structure
                    if 'response' in data or 'message' in data:
                        response.success()
                    else:
                        response.failure(f"Invalid response structure: {data}")
                elif response.status_code == 500:
                    # API returned error but we got a response
                    response.failure(f"Server error: {response.text[:200]}")
                else:
                    response.failure(f"Unexpected status: {response.status_code}")
            except json.JSONDecodeError:
                response.failure(f"Invalid JSON response: {response.text[:200]}")
            except Exception as e:
                response.failure(f"Request failed: {str(e)}")
    
    @task(1)
    def health_check(self):
        """Check API health (10% of requests)"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


class QuoteFlowUser(HttpUser):
    """Simulates a user going through complete quote flow"""
    
    wait_time = between(3, 7)
    
    def on_start(self):
        """Initialize user session"""
        self.session_id = f"quote_flow_{random.randint(10000, 99999)}"
        self.current_step = 0
    
    @task
    def complete_quote_flow(self):
        """Simulate complete quote conversation"""
        flow_steps = [
            "Hola",
            "Necesito una cotización",
            "Isodec 100mm",
            "10 metros por 5 metros",
            "Juan Pérez, 099123456"
        ]
        
        if self.current_step < len(flow_steps):
            message = flow_steps[self.current_step]
            
            with self.client.post(
                "/api/chat",
                json={
                    "message": message,
                    "session_id": self.session_id
                },
                catch_response=True,
                name=f"/api/chat/quote_flow_step_{self.current_step + 1}"
            ) as response:
                if response.status_code == 200:
                    response.success()
                    self.current_step += 1
                else:
                    response.failure(f"Flow failed at step {self.current_step + 1}")
        else:
            # Reset for next iteration
            self.current_step = 0
            self.session_id = f"quote_flow_{random.randint(10000, 99999)}"


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start"""
    print(f"\n{'='*60}")
    print(f"Starting load test at {datetime.now()}")
    print(f"Target host: {environment.host}")
    print(f"{'='*60}\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test results"""
    stats = environment.stats
    
    print(f"\n{'='*60}")
    print(f"Load test completed at {datetime.now()}")
    print(f"{'='*60}")
    print(f"\n📊 Summary:")
    print(f"  Total requests: {stats.total.num_requests}")
    print(f"  Failed requests: {stats.total.num_failures}")
    print(f"  Failure rate: {stats.total.fail_ratio*100:.2f}%")
    print(f"  Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"  95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"  99th percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"  Requests/second: {stats.total.total_rps:.2f}")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    import subprocess
    subprocess.run([
        "locust", "-f", "locustfile.py",
        "--headless", "-u", "10", "-r", "2",
        "-t", "1m", "--host", "http://localhost:8000"
    ], check=False)
