export const dynamic = 'force-dynamic';

<<<<<<< Updated upstream
import { NextRequest, NextResponse } from 'next/server'
import { quoteEngine } from '@/lib/quote-engine'
import { parseQuoteConsulta } from '@/lib/quote-parser'
import { initializeBMCSystem } from '@/lib/initialize-system'
=======
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { initializeBMCSystem } from '@/lib/initialize-system'
import { quoteEngine } from '@/lib/quote-engine'
import { parseQuoteConsulta } from '@/lib/quote-parser'
import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
      return NextResponse.json({ 
        success: false,
        error: 'message is required and must be a string' 
      }, { status: 400 })
=======
      return validationErrorResponse(
        ['message is required and must be a string'],
        'Invalid request'
      )
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    
    return NextResponse.json({
      success: true,
      data: {
        response,
        parsedData,
        sessionId,
        userPhone,
        timestamp: new Date().toISOString()
      }
=======

    return successResponse({
      response,
      parsedData,
      sessionId,
      userPhone,
      timestamp: new Date().toISOString(),
>>>>>>> Stashed changes
    })
  } catch (error: unknown) {
    console.error('Error in chat API:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      data: {
        tipo: 'error',
        mensaje: 'Lo siento, hubo un problema procesando tu mensaje. Por favor, intenta de nuevo.'
      }
    }, { status: 500 })
=======
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(
      errorMessage,
      500,
      'Lo siento, hubo un problema procesando tu mensaje. Por favor, intenta de nuevo.'
    )
>>>>>>> Stashed changes
  }
}

// Endpoint para obtener información de productos
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = searchParams.get('q')
    const tipo = searchParams.get('tipo') || 'all'
    
    if (!query) {
<<<<<<< Updated upstream
      return NextResponse.json({ 
        success: false,
        error: 'query parameter is required' 
      }, { status: 400 })
=======
      return validationErrorResponse(
        ['query parameter is required'],
        'Missing required parameter'
      )
>>>>>>> Stashed changes
    }
    
    // Procesar consulta
    const response = await quoteEngine.procesarConsulta(query)
<<<<<<< Updated upstream
    
    return NextResponse.json({
      success: true,
      data: response,
=======

    return successResponse({
      response,
>>>>>>> Stashed changes
      query,
      tipo,
      timestamp: new Date().toISOString()
    })
  } catch (error: unknown) {
    console.error('Error in chat GET:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}
