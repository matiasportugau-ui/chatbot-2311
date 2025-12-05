export const dynamic = 'force-dynamic';


import { initializeBMCSystem } from '@/lib/initialize-system'
import { getMotorCotizacionIntegrado } from '@/lib/integrated-quote-engine'
import { NextRequest } from 'next/server'
import {
  successResponse,
  errorResponse,
  validationErrorResponse,
} from '@/lib/api-response'


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

/**
 * 🧠 API Endpoint para Motor de Cotización Integrado
 * 
 * Este endpoint integra el sistema de cotización con la base de conocimiento
 * evolutiva que aprende de cada interacción.
 */

export async function POST(request: NextRequest) {
  try {
    await ensureSystemInitialized()
    
    const { consulta, userPhone, userName, action } = await request.json()
    
    if (!consulta || !userPhone) {

      return validationErrorResponse(
        ['Missing required parameters: consulta, userPhone'],
        'Missing required fields'
      )

    }

    switch (action) {
      case 'process':
        return await procesarConsulta(consulta, userPhone, userName)
      
      case 'metrics':
        return await obtenerMetricas()
      
      case 'update_knowledge':
        return await actualizarBaseConocimiento()
      
      case 'analyze_patterns':
        return await analizarPatrones()
      
      default:

        return validationErrorResponse(
          ['Invalid action. Use: process, metrics, update_knowledge, analyze_patterns'],
          'Invalid action parameter'
        )

    }
  } catch (error: any) {
    console.error('Error in integrated-quote API:', error)

    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Internal server error', 500, errorMessage)

  }
}

/**
 * 🔄 Procesar Consulta con IA Integrada
 */
async function procesarConsulta(consulta: string, userPhone: string, userName?: string) {
  try {
    const motorCotizacionIntegrado = await getMotorCotizacionIntegrado()
    const respuesta = await motorCotizacionIntegrado.procesarConsulta(
      consulta, 
      userPhone, 
      userName
    )


    return successResponse({
      respuesta,
      timestamp: new Date().toISOString(),
      session_id: `sess_${Date.now()}`,
      user_phone: userPhone,

    })
  } catch (error: any) {
    console.error('Error procesando consulta:', error)

    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error procesando consulta', 500, errorMessage)

  }
}

/**
 * 📊 Obtener Métricas del Sistema
 */
async function obtenerMetricas() {
  try {
    const motorCotizacionIntegrado = await getMotorCotizacionIntegrado()
    const metricas = await motorCotizacionIntegrado.obtenerMetricas()


    return successResponse({
      metricas,
      timestamp: new Date().toISOString(),
      status: 'active',

    })
  } catch (error: any) {
    console.error('Error obteniendo métricas:', error)

    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error obteniendo métricas', 500, errorMessage)

  }
}

/**
 * 🧠 Actualizar Base de Conocimiento
 */
async function actualizarBaseConocimiento() {
  try {
    const motorCotizacionIntegrado = await getMotorCotizacionIntegrado()
    await motorCotizacionIntegrado.actualizarBaseConocimiento()


    return successResponse(
      { updated: true, timestamp: new Date().toISOString() },
      'Base de conocimiento actualizada correctamente'
    )
  } catch (error: unknown) {
    console.error('Error actualizando base de conocimiento:', error)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error actualizando base de conocimiento', 500, errorMessage)

  }
}

/**
 * 🔍 Analizar Patrones de Venta
 */
async function analizarPatrones() {
  try {
    // Esta función podría implementar análisis más avanzados
    const motorCotizacionIntegrado = await getMotorCotizacionIntegrado()
    const metricas = await motorCotizacionIntegrado.obtenerMetricas()


    return successResponse({
      patrones_identificados: metricas.patrones_identificados,
      productos_mas_consultados: 'Análisis en desarrollo',
      zonas_mas_activas: 'Análisis en desarrollo',
      horarios_pico: 'Análisis en desarrollo',
      timestamp: new Date().toISOString(),

    })
  } catch (error: any) {
    console.error('Error analizando patrones:', error)

    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error analizando patrones', 500, errorMessage)

  }
}

/**
 * GET - Obtener información del sistema
 */
export async function GET(request: NextRequest) {
  try {
    await ensureSystemInitialized()
    
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action') || 'info'
    
    switch (action) {
      case 'info':

        return successResponse({
          name: 'Motor de Cotización Integrado BMC',
          version: '1.0.0',
          description:
            'Sistema de cotización con base de conocimiento evolutiva',
          features: [
            'IA Conversacional Inteligente',
            'Base de Conocimiento Dinámica',
            'Análisis de Patrones de Venta',
            'Personalización por Cliente',
            'Aprendizaje Automático',
            'Métricas en Tiempo Real',
          ],
          endpoints: {
            'POST /api/integrated-quote': {
              actions: [
                'process',
                'metrics',
                'update_knowledge',
                'analyze_patterns',
              ],
            },
          },
          timestamp: new Date().toISOString(),

        })
      
      case 'health':

        return successResponse({
          status: 'healthy',
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          timestamp: new Date().toISOString(),

        })
      
      default:

        return validationErrorResponse(
          ['Invalid action. Use: info, health'],
          'Invalid action parameter'
        )

    }
  } catch (error: any) {
    console.error('Error in integrated-quote GET:', error)

    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Internal server error', 500, errorMessage)

  }
}
