export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server'
import { quoteEngine } from '@/lib/quote-engine'

export async function POST(request: NextRequest) {
  try {
    const { consulta, telefono, includeMetadata = false } = await request.json()
    
    if (!consulta || typeof consulta !== 'string') {
      return NextResponse.json({ 
        success: false,
        error: 'consulta is required and must be a string' 
      }, { status: 400 })
    }
    
    // Procesar consulta con motor de cotización
    const response = await quoteEngine.procesarConsulta(consulta, telefono)
    
    // Agregar metadata si se solicita
    const result = {
      success: true,
      data: response,
      ...(includeMetadata && {
        metadata: {
          timestamp: new Date().toISOString(),
          consulta_original: consulta,
          telefono: telefono || null,
          procesado_por: 'quote-engine-v1.0'
        }
      })
    }
    
    return NextResponse.json(result)
  } catch (error) {
    console.error('Error in quote-engine API:', error)
    return NextResponse.json({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      data: {
        tipo: 'error',
        mensaje: 'Error interno del sistema. Por favor, intenta de nuevo.'
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
    
    // Buscar productos
    const response = await quoteEngine.procesarConsulta(query)
    
    return NextResponse.json({
      success: true,
      data: response,
      query,
      tipo
    })
  } catch (error) {
    console.error('Error in quote-engine GET:', error)
    return NextResponse.json({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
  }
}
