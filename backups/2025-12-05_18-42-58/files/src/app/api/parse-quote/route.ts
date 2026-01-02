export const dynamic = 'force-dynamic';


import {
  extractContactInfo,
  isValidQuoteRequest,
  parseQuoteConsulta,
} from '@/lib/quote-parser'
import { NextRequest } from 'next/server'
import {
  successResponse,
  errorResponse,
  validationErrorResponse,
} from '@/lib/api-response'


export async function POST(request: NextRequest) {
  try {
    const { consultaText, includeContactInfo = false } = await request.json()
    
    if (!consultaText || typeof consultaText !== 'string') {

      return validationErrorResponse(
        ['consultaText is required and must be a string'],
        'Invalid request'
      )

    }
    
    // Validar si es una consulta válida
    const isValid = isValidQuoteRequest(consultaText)
    
    if (!isValid) {

      return successResponse({
        isValid: false,
        message: 'El texto no parece ser una consulta de cotización válida',

      })
    }
    
    // Parsear consulta con IA
    const parsed = await parseQuoteConsulta(consultaText)
    
    // Extraer información de contacto si se solicita
    let contactInfo = null
    if (includeContactInfo) {
      contactInfo = extractContactInfo(consultaText)
    }


    return successResponse({
      isValid: true,
      parsed,
      contactInfo,
      originalText: consultaText,
      timestamp: new Date().toISOString(),

    })
  } catch (error: unknown) {
    console.error('Error in parse-quote API:', error)

    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)

  }
}

// Endpoint para validar si un texto es una consulta válida
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const text = searchParams.get('text')
    
    if (!text) {

      return validationErrorResponse(
        ['text parameter is required'],
        'Missing required parameter'
      )

    }
    
    const isValid = isValidQuoteRequest(text)
    const contactInfo = extractContactInfo(text)


    return successResponse({
      isValid,
      contactInfo,
      text,

    })
  } catch (error: unknown) {
    console.error('Error in parse-quote GET:', error)

    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)

  }
}
