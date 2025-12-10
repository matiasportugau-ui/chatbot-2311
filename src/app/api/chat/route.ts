import { NextRequest } from 'next/server';
import { getMotorCotizacionIntegrado } from '@/lib/integrated-quote-engine';
import { initializeBMCSystem } from '@/lib/initialize-system';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

let systemInitialized = false;

async function ensureSystemInitialized() {
  if (!systemInitialized) {
    const result = await initializeBMCSystem();
    if (result.success) {
      systemInitialized = true;
    } else {
      console.warn('Sistema inicializado con advertencias:', result);
      systemInitialized = true; // Continue anyway
    }
  }
}

/**
 * API endpoint para el chat conversacional con IA
 */
export async function POST(req: NextRequest) {
  try {
    await ensureSystemInitialized();

    const body = await req.json();
    const { messages, sessionId } = body;

    if (!messages || messages.length === 0) {
      return new Response(
        JSON.stringify({ error: 'No messages provided' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Get the last user message
    const lastMessage = messages[messages.length - 1];
    const userPhone = body.userPhone || '+59899999999';
    const userName = body.userName || 'Cliente';

    // Process the query using the integrated quote engine
    const motorCotizacionIntegrado = await getMotorCotizacionIntegrado();
    const respuesta = await motorCotizacionIntegrado.procesarConsulta(
      lastMessage.content,
      userPhone,
      userName
    );

    // Format response for the chat interface
    const responseText = respuesta.mensaje;

    // Set confidence header if available
    const headers = new Headers({
      'Content-Type': 'text/plain; charset=utf-8',
    });

    if (respuesta.confianza !== undefined) {
      headers.set('X-Confidence', respuesta.confianza.toString());
    }

    if (respuesta.tipo) {
      headers.set('X-Source', respuesta.tipo);
    }

    // Return as a streaming response for better UX
    const stream = new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder();
        controller.enqueue(encoder.encode(responseText));
        controller.close();
      },
    });

    return new Response(stream, { headers });

  } catch (error) {
    console.error('Error in chat API:', error);

    // Return a user-friendly error message
    const errorMessage = error instanceof Error
      ? `Error: ${error.message}`
      : 'Ha ocurrido un error inesperado. Por favor, intenta de nuevo.';

    return new Response(errorMessage, {
      status: 500,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  }
}
