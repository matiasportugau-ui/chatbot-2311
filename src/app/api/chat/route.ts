import { NextRequest, NextResponse } from 'next/server'
import { quoteEngine } from '@/lib/quote-engine'
import { parseQuoteConsulta } from '@/lib/quote-parser'
import { initializeBMCSystem } from '@/lib/initialize-system'

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
      return NextResponse.json({ 
        success: false,
        error: 'message is required and must be a string' 
      }, { status: 400 })
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
    
    return NextResponse.json({
      success: true,
      data: {
        response,
        parsedData,
        sessionId,
        userPhone,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error) {
    console.error('Error in chat API:', error)
    return NextResponse.json({ 
      success: false,
      error: error.message,
      data: {
        tipo: 'error',
        mensaje: 'Lo siento, hubo un problema procesando tu mensaje. Por favor, intenta de nuevo.'
      }
    }, { status: 500 })
  }
}

// Endpoint para obtener información de productos
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = searchParams.get('q')
    const tipo = searchParams.get('tipo') || 'all'
    
    if (!query) {
      return NextResponse.json({ 
        success: false,
        error: 'query parameter is required' 
      }, { status: 400 })
    }
    
    // Procesar consulta
    const response = await quoteEngine.procesarConsulta(query)
    
    return NextResponse.json({
      success: true,
      data: response,
      query,
      tipo,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error in chat GET:', error)
    return NextResponse.json({ 
      success: false,
      error: error.message 
    }, { status: 500 })
  }
}
