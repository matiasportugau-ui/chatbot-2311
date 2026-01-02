
const PY_API_URL = process.env.PY_CHAT_SERVICE_URL || 'http://localhost:8000';
const INTERNAL_API_KEY = process.env.INTERNAL_API_KEY || 'bmc_int_9e72b4f18a2c03d5';

async function testChatEndpoint() {
  console.log('Testing /api/chat endpoint...');
  
  try {
    const response = await fetch(`${PY_API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': INTERNAL_API_KEY,
      },
      body: JSON.stringify({
        message: "Hola, ¿tienen stock de Isodec?",
        session_id: "test_session_123"
      }),
    });

    if (!response.ok) {
      console.error(`Status: ${response.status}`);
      const text = await response.text();
      console.error('Body:', text);
      return;
    }

    const data = await response.json();
    console.log('Response:', data);

    if (data.response && data.session_id) {
      console.log('✅ /api/chat contract verified success!');
    } else {
      console.error('❌ Response schema mismatch. Expected response and session_id.');
    }

  } catch (error) {
    console.error('Error:', error);
  }
}

testChatEndpoint();
