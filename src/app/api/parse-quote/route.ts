export const dynamic = 'force-dynamic';

<<<<<<< Updated upstream
import { NextRequest, NextResponse } from 'next/server'
import { parseQuoteConsulta, isValidQuoteRequest, extractContactInfo } from '@/lib/quote-parser'
=======
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
>>>>>>> Stashed changes

export async function POST(request: NextRequest) {
  try {
    const { consultaText, includeContactInfo = false } = await request.json()
    
    if (!consultaText || typeof consultaText !== 'string') {
<<<<<<< Updated upstream
      return NextResponse.json({ 
        success: false,
        error: 'consultaText is required and must be a string' 
      }, { status: 400 })
=======
      return validationErrorResponse(
        ['consultaText is required and must be a string'],
        'Invalid request'
      )
>>>>>>> Stashed changes
    }
    
    // Validar si es una consulta válida
    const isValid = isValidQuoteRequest(consultaText)
    
    if (!isValid) {
<<<<<<< Updated upstream
      return NextResponse.json({
        success: true,
        data: {
          isValid: false,
          message: 'El texto no parece ser una consulta de cotización válida'
        }
=======
      return successResponse({
        isValid: false,
        message: 'El texto no parece ser una consulta de cotización válida',
>>>>>>> Stashed changes
      })
    }
    
    // Parsear consulta con IA
    const parsed = await parseQuoteConsulta(consultaText)
    
    // Extraer información de contacto si se solicita
    let contactInfo = null
    if (includeContactInfo) {
      contactInfo = extractContactInfo(consultaText)
    }
<<<<<<< Updated upstream
    
    return NextResponse.json({ 
      success: true, 
      data: {
        isValid: true,
        parsed,
        contactInfo,
        originalText: consultaText,
        timestamp: new Date().toISOString()
      }
=======

    return successResponse({
      isValid: true,
      parsed,
      contactInfo,
      originalText: consultaText,
      timestamp: new Date().toISOString(),
>>>>>>> Stashed changes
    })
  } catch (error: unknown) {
    console.error('Error in parse-quote API:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}

// Endpoint para validar si un texto es una consulta válida
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const text = searchParams.get('text')
    
    if (!text) {
<<<<<<< Updated upstream
      return NextResponse.json({ 
        success: false,
        error: 'text parameter is required' 
      }, { status: 400 })
=======
      return validationErrorResponse(
        ['text parameter is required'],
        'Missing required parameter'
      )
>>>>>>> Stashed changes
    }
    
    const isValid = isValidQuoteRequest(text)
    const contactInfo = extractContactInfo(text)
<<<<<<< Updated upstream
    
    return NextResponse.json({
      success: true,
      data: {
        isValid,
        contactInfo,
        text
      }
=======

    return successResponse({
      isValid,
      contactInfo,
      text,
>>>>>>> Stashed changes
    })
  } catch (error: unknown) {
    console.error('Error in parse-quote GET:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}
