import { NextRequest, NextResponse } from 'next/server'
import { parseQuoteConsulta, isValidQuoteRequest, extractContactInfo } from '@/lib/quote-parser'

export async function POST(request: NextRequest) {
  try {
    const { consultaText, includeContactInfo = false } = await request.json()
    
    if (!consultaText || typeof consultaText !== 'string') {
      return NextResponse.json({ 
        success: false,
        error: 'consultaText is required and must be a string' 
      }, { status: 400 })
    }
    
    // Validar si es una consulta válida
    const isValid = isValidQuoteRequest(consultaText)
    
    if (!isValid) {
      return NextResponse.json({
        success: true,
        data: {
          isValid: false,
          message: 'El texto no parece ser una consulta de cotización válida'
        }
      })
    }
    
    // Parsear consulta con IA
    const parsed = await parseQuoteConsulta(consultaText)
    
    // Extraer información de contacto si se solicita
    let contactInfo = null
    if (includeContactInfo) {
      contactInfo = extractContactInfo(consultaText)
    }
    
    return NextResponse.json({ 
      success: true, 
      data: {
        isValid: true,
        parsed,
        contactInfo,
        originalText: consultaText,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error) {
    console.error('Error in parse-quote API:', error)
    return NextResponse.json({ 
      success: false,
      error: error.message 
    }, { status: 500 })
  }
}

// Endpoint para validar si un texto es una consulta válida
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const text = searchParams.get('text')
    
    if (!text) {
      return NextResponse.json({ 
        success: false,
        error: 'text parameter is required' 
      }, { status: 400 })
    }
    
    const isValid = isValidQuoteRequest(text)
    const contactInfo = extractContactInfo(text)
    
    return NextResponse.json({
      success: true,
      data: {
        isValid,
        contactInfo,
        text
      }
    })
  } catch (error) {
    console.error('Error in parse-quote GET:', error)
    return NextResponse.json({ 
      success: false,
      error: error.message 
    }, { status: 500 })
  }
}
