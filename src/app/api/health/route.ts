import { NextResponse } from 'next/server'
import { initializeSimpleSystem, getSystemStatus } from '@/lib/simple-initialize'

/**
 * Health Check Endpoint Simplificado
 * Verifica el estado de todos los servicios del sistema BMC
 */
export async function GET() {
  try {
    const result = await initializeSimpleSystem()
    
    const services = {
      openai: {
        configured: !!process.env.OPENAI_API_KEY,
        status: process.env.OPENAI_API_KEY ? 'ready' : 'missing'
      },
      googleSheets: {
        configured: !!(process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL && process.env.GOOGLE_PRIVATE_KEY),
        sheetId: process.env.GOOGLE_SHEET_ID || 'not configured',
        status: (process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL && process.env.GOOGLE_PRIVATE_KEY) ? 'ready' : 'missing'
      },
      mongodb: {
        configured: !!process.env.MONGODB_URI,
        status: process.env.MONGODB_URI ? 'ready' : 'missing'
      },
      whatsapp: {
        configured: !!(process.env.WHATSAPP_ACCESS_TOKEN && process.env.WHATSAPP_PHONE_NUMBER_ID),
        status: (process.env.WHATSAPP_ACCESS_TOKEN && process.env.WHATSAPP_PHONE_NUMBER_ID) ? 'ready' : 'optional'
      }
    }
    
    const allCriticalServicesReady = services.openai.configured && 
                                     services.googleSheets.configured && 
                                     services.mongodb.configured
    
    return NextResponse.json({
      status: allCriticalServicesReady ? 'healthy' : 'partial',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      services,
      initialization: result,
      systemStatus: getSystemStatus(),
      message: allCriticalServicesReady 
        ? 'All critical services are configured and ready'
        : 'Some services need configuration'
    })
  } catch (error: any) {
    return NextResponse.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    }, { status: 500 })
  }
}

