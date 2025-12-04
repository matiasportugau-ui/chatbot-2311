export const dynamic = 'force-dynamic';

<<<<<<< Updated upstream
import { NextRequest, NextResponse } from 'next/server'
import { quoteEngine } from '@/lib/quote-engine'
=======
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { quoteEngine } from '@/lib/quote-engine'
import { NextRequest } from 'next/server'
>>>>>>> Stashed changes

export async function POST(request: NextRequest) {
  try {
    const { consulta, telefono, includeMetadata = false } = await request.json()
    
    if (!consulta || typeof consulta !== 'string') {
<<<<<<< Updated upstream
      return NextResponse.json({ 
        success: false,
        error: 'consulta is required and must be a string' 
      }, { status: 400 })
=======
      return validationErrorResponse(
        ['consulta is required and must be a string'],
        'Invalid request'
      )
>>>>>>> Stashed changes
    }
    
    // Procesar consulta con motor de cotización
    const response = await quoteEngine.procesarConsulta(consulta, telefono)
    
    // Agregar metadata si se solicita
<<<<<<< Updated upstream
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
=======
    const result: {
      response: unknown
      metadata?: {
        timestamp: string
        consulta_original: string
        telefono: string | null
        procesado_por: string
      }
    } = {
      response,
    }

    if (includeMetadata) {
      result.metadata = {
        timestamp: new Date().toISOString(),
        consulta_original: consulta,
        telefono: telefono || null,
        procesado_por: 'quote-engine-v1.0',
      }
    }

    return successResponse(result)
  } catch (error: unknown) {
    console.error('Error in quote-engine API:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(
      errorMessage,
      500,
      'Error interno del sistema. Por favor, intenta de nuevo.'
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
    
    // Buscar productos
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
      tipo
    })
  } catch (error: unknown) {
    console.error('Error in quote-engine GET:', error)
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
