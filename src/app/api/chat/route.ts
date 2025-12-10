import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function POST(req: NextRequest) {
  try {
    const { messages, sessionId } = await req.json();

    // Call the Python backend
    // Assuming the Python backend is running on port 8000 locally
    // In production, this URL should be an environment variable
    const backendUrl = process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:8000';

    const response = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        sessionId: sessionId || 'default'
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return new Response(errorText, { status: response.status });
    }

    // Pass the stream through
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Transfer-Encoding': 'chunked',
      },
    });

  } catch (error) {
    console.error('Error in chat proxy:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}
