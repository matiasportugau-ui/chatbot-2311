export const dynamic = 'force-dynamic';

import { NextRequest } from 'next/server'
import { quoteEngine } from '@/lib/quote-engine'
import { parseQuoteConsulta } from '@/lib/quote-parser'
import { initializeBMCSystem } from '@/lib/initialize-system'

// Initialize system if not ready
let systemInitialized = false
async function ensureSystemInitialized() {
  if (!systemInitialized) {
    const result = await initializeBMCSystem()
    if (result.success) {
      systemInitialized = true
    } else {
      throw new Error(`Sistema no inicializado: ${result.error}`)
    }
  }
}

// Simple streaming response compatible with useChat
function createStreamResponse(text: string, metadata?: Record<string, string>) {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      // Split text into chunks for streaming effect
      const words = text.split(' ')
      for (let i = 0; i < words.length; i++) {
        const chunk = (i === 0 ? '' : ' ') + words[i]
        controller.enqueue(encoder.encode(chunk))
        // Small delay for streaming effect
        await new Promise(resolve => setTimeout(resolve, 20))
      }
      controller.close()
    }
  })

  const headers = new Headers({
    'Content-Type': 'text/plain; charset=utf-8',
    ...metadata
  })

  return new Response(stream, { headers })
}

export async function POST(request: NextRequest) {
  let sessionId: string | null = null
  try {
    await ensureSystemInitialized()
    
    const { messages, data } = await request.json()
    
    // Get the last user message
    const lastMessage = messages[messages.length - 1]
    if (!lastMessage || !lastMessage.content) {
      throw new Error('No message content provided')
    }

    const userMessage = lastMessage.content
    const userPhone = data?.userPhone || '+59891234567'
    sessionId = data?.sessionId || null

    // Process message with quote engine
    const quoteResponse = await quoteEngine.procesarConsulta(userMessage, userPhone)
    
    // Parse quote data if it's a quote request
    let parsedData = null
    if (quoteResponse.tipo === 'cotizacion') {
      try {
        parsedData = await parseQuoteConsulta(userMessage)
      } catch (error) {
        console.log('Error parsing quote data:', error)
      }
    }

    // Build response text with all information
    let responseText = quoteResponse.mensaje

    // Add quote details if available
    if (quoteResponse.cotizacion) {
      responseText += `\n\n💰 **Cotización Generada:**\n`
      responseText += `- Producto: ${quoteResponse.cotizacion.producto}\n`
      responseText += `- Descripción: ${quoteResponse.cotizacion.descripcion}\n`
      if (quoteResponse.cotizacion.precio_base) {
        responseText += `- Precio Base: $${quoteResponse.cotizacion.precio_base.toLocaleString()}\n`
      }
      if (quoteResponse.cotizacion.total) {
        responseText += `- Total: $${quoteResponse.cotizacion.total.toLocaleString()}\n`
      }
      if (quoteResponse.cotizacion.codigo) {
        responseText += `- Código: ${quoteResponse.cotizacion.codigo}\n`
      }
    }

    // Add product suggestions if available
    if (quoteResponse.productos_sugeridos && quoteResponse.productos_sugeridos.length > 0) {
      responseText += `\n\n🏗️ **Productos Sugeridos:**\n`
      quoteResponse.productos_sugeridos.forEach((producto, index) => {
        responseText += `${index + 1}. ${producto.nombre}`
        if (producto.descripcion) {
          responseText += ` - ${producto.descripcion}`
        }
        if (producto.precio_estimado) {
          responseText += ` ($${producto.precio_estimado}/m²)`
        }
        responseText += '\n'
      })
    }

    // Add FAQs if available
    if (quoteResponse.preguntas_frecuentes && quoteResponse.preguntas_frecuentes.length > 0) {
      responseText += `\n\n❓ **Preguntas Relacionadas:**\n`
      quoteResponse.preguntas_frecuentes.forEach((faq, index) => {
        responseText += `${index + 1}. ${faq.pregunta}\n   ${faq.respuesta}\n`
      })
    }

    // Return streaming response with metadata
    const headers: Record<string, string> = {
      'X-Quote-Type': quoteResponse.tipo,
      'X-Session-Id': sessionId || '',
    }
    
    // Add confidence header if available from parsed data
    if (parsedData && typeof parsedData.confianza === 'number' && !isNaN(parsedData.confianza) && isFinite(parsedData.confianza)) {
      headers['X-Confidence'] = parsedData.confianza.toString()
    }
    
    return createStreamResponse(responseText, headers)
  } catch (error) {
    console.error('Error in streaming chat API:', error)
    
    // Return error message
    const errorMessage = error instanceof Error 
      ? error.message 
      : 'Lo siento, hubo un problema procesando tu mensaje. Por favor, intenta de nuevo.'
    
    return createStreamResponse(
      `Lo siento, hubo un error al procesar tu consulta: ${errorMessage}\n\nPor favor, intenta reformular tu pregunta o contacta con soporte.`,
      {
        'X-Error': 'true',
        'X-Session-Id': sessionId || '',
      }
    )
  }
}