
import requests
import json
import hmac
import hashlib
import time

def send_test_message():
    url = "http://localhost:5001/webhook"
    secret = "0feb99dd58f6067c890067317b6bff6d"
    
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "1344290740770002",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "1234567890",
                        "phone_number_id": "1344290740770002"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Test User"
                        },
                        "wa_id": "59891234567"
                    }],
                    "messages": [{
                        "from": "59891234567",
                        "id": "wamid.test",
                        "timestamp": str(int(time.time())),
                        "text": {
                            "body": "Hola, necesito cotizar isodec"
                        },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    payload_json = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}"
    }
    
    print(f"Sending webhook to {url}...")
    try:
        response = requests.post(url, data=payload_json, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_test_message()
