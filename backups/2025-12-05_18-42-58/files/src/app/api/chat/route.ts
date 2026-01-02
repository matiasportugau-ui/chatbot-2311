export const dynamic = 'force-dynamic';

import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { initializeBMCSystem } from '@/lib/initialize-system'
import { quoteEngine } from '@/lib/quote-engine'
import { parseQuoteConsulta } from '@/lib/quote-parser'
import { NextRequest } from 'next/server'

// Inicializar sistema si no está listo
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

export async function POST(request: NextRequest) {
  try {
    const { message, sessionId, userPhone } = await request.json()

    if (!message || typeof message !== 'string') {
      return validationErrorResponse(
        ['message is required and must be a string'],
        'Invalid request'
      )
    }

    // Procesar mensaje con motor de cotización BMC
    const response = await quoteEngine.procesarConsulta(message, userPhone)

    // Si es una cotización, también parsear para extraer datos estructurados
    let parsedData = null
    if (response.tipo === 'cotizacion') {
      try {
        parsedData = await parseQuoteConsulta(message)
      } catch (error) {
        console.log('Error parsing quote data:', error)
      }
    }

    return successResponse({
      response,
      parsedData,
      sessionId,
      userPhone,
      timestamp: new Date().toISOString(),
    })
  } catch (error: unknown) {
    console.error('Error in chat API:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(
      errorMessage,
      500,
      'Lo siento, hubo un problema procesando tu mensaje. Por favor, intenta de nuevo.'
    )
  }
}

// Endpoint para obtener información de productos
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = searchParams.get('q')
    const tipo = searchParams.get('tipo') || 'all'

    if (!query) {
      return validationErrorResponse(
        ['query parameter is required'],
        'Missing required parameter'
      )
    }

    // Procesar consulta
    const response = await quoteEngine.procesarConsulta(query)

    return successResponse({
      response,
      query,
      tipo,
      timestamp: new Date().toISOString()
    })
  } catch (error: unknown) {
    console.error('Error in chat GET:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)
  }
}
