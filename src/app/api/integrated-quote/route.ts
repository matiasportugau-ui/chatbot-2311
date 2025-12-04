export const dynamic = 'force-dynamic';

<<<<<<< Updated upstream
import { NextRequest, NextResponse } from 'next/server'
import { getMotorCotizacionIntegrado } from '@/lib/integrated-quote-engine'
import { initializeBMCSystem } from '@/lib/initialize-system'
=======
import { initializeBMCSystem } from '@/lib/initialize-system'
import { getMotorCotizacionIntegrado } from '@/lib/integrated-quote-engine'
import { NextRequest } from 'next/server'
import {
  successResponse,
  errorResponse,
  validationErrorResponse,
} from '@/lib/api-response'
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
      return NextResponse.json({ 
        error: 'Missing required parameters: consulta, userPhone' 
      }, { status: 400 })
=======
      return validationErrorResponse(
        ['Missing required parameters: consulta, userPhone'],
        'Missing required fields'
      )
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        return NextResponse.json({ 
          error: 'Invalid action. Use: process, metrics, update_knowledge, analyze_patterns' 
        }, { status: 400 })
=======
        return validationErrorResponse(
          ['Invalid action. Use: process, metrics, update_knowledge, analyze_patterns'],
          'Invalid action parameter'
        )
>>>>>>> Stashed changes
    }
  } catch (error: any) {
    console.error('Error in integrated-quote API:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      error: 'Internal server error', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Internal server error', 500, errorMessage)
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    
    return NextResponse.json({
      success: true,
      data: {
        respuesta,
        timestamp: new Date().toISOString(),
        session_id: `sess_${Date.now()}`,
        user_phone: userPhone
      }
=======

    return successResponse({
      respuesta,
      timestamp: new Date().toISOString(),
      session_id: `sess_${Date.now()}`,
      user_phone: userPhone,
>>>>>>> Stashed changes
    })
  } catch (error: any) {
    console.error('Error procesando consulta:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      error: 'Error procesando consulta', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error procesando consulta', 500, errorMessage)
>>>>>>> Stashed changes
  }
}

/**
 * 📊 Obtener Métricas del Sistema
 */
async function obtenerMetricas() {
  try {
    const motorCotizacionIntegrado = await getMotorCotizacionIntegrado()
    const metricas = await motorCotizacionIntegrado.obtenerMetricas()
<<<<<<< Updated upstream
    
    return NextResponse.json({
      success: true,
      data: {
        metricas,
        timestamp: new Date().toISOString(),
        status: 'active'
      }
=======

    return successResponse({
      metricas,
      timestamp: new Date().toISOString(),
      status: 'active',
>>>>>>> Stashed changes
    })
  } catch (error: any) {
    console.error('Error obteniendo métricas:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      error: 'Error obteniendo métricas', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error obteniendo métricas', 500, errorMessage)
>>>>>>> Stashed changes
  }
}

/**
 * 🧠 Actualizar Base de Conocimiento
 */
async function actualizarBaseConocimiento() {
  try {
    const motorCotizacionIntegrado = await getMotorCotizacionIntegrado()
    await motorCotizacionIntegrado.actualizarBaseConocimiento()
<<<<<<< Updated upstream
    
    return NextResponse.json({
      success: true,
      message: 'Base de conocimiento actualizada correctamente',
      timestamp: new Date().toISOString()
    })
  } catch (error: any) {
    console.error('Error actualizando base de conocimiento:', error)
    return NextResponse.json({ 
      error: 'Error actualizando base de conocimiento', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======

    return successResponse(
      { updated: true, timestamp: new Date().toISOString() },
      'Base de conocimiento actualizada correctamente'
    )
  } catch (error: unknown) {
    console.error('Error actualizando base de conocimiento:', error)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error actualizando base de conocimiento', 500, errorMessage)
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    
    return NextResponse.json({
      success: true,
      data: {
        patrones_identificados: metricas.patrones_identificados,
        productos_mas_consultados: 'Análisis en desarrollo',
        zonas_mas_activas: 'Análisis en desarrollo',
        horarios_pico: 'Análisis en desarrollo',
        timestamp: new Date().toISOString()
      }
=======

    return successResponse({
      patrones_identificados: metricas.patrones_identificados,
      productos_mas_consultados: 'Análisis en desarrollo',
      zonas_mas_activas: 'Análisis en desarrollo',
      horarios_pico: 'Análisis en desarrollo',
      timestamp: new Date().toISOString(),
>>>>>>> Stashed changes
    })
  } catch (error: any) {
    console.error('Error analizando patrones:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      error: 'Error analizando patrones', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Error analizando patrones', 500, errorMessage)
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        return NextResponse.json({
          success: true,
          data: {
            name: 'Motor de Cotización Integrado BMC',
            version: '1.0.0',
            description: 'Sistema de cotización con base de conocimiento evolutiva',
            features: [
              'IA Conversacional Inteligente',
              'Base de Conocimiento Dinámica',
              'Análisis de Patrones de Venta',
              'Personalización por Cliente',
              'Aprendizaje Automático',
              'Métricas en Tiempo Real'
            ],
            endpoints: {
              'POST /api/integrated-quote': {
                actions: ['process', 'metrics', 'update_knowledge', 'analyze_patterns']
              }
            },
            timestamp: new Date().toISOString()
          }
=======
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
>>>>>>> Stashed changes
        })
      
      case 'health':
<<<<<<< Updated upstream
        return NextResponse.json({
          success: true,
          data: {
            status: 'healthy',
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            timestamp: new Date().toISOString()
          }
=======
        return successResponse({
          status: 'healthy',
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          timestamp: new Date().toISOString(),
>>>>>>> Stashed changes
        })
      
      default:
<<<<<<< Updated upstream
        return NextResponse.json({ 
          error: 'Invalid action. Use: info, health' 
        }, { status: 400 })
=======
        return validationErrorResponse(
          ['Invalid action. Use: info, health'],
          'Invalid action parameter'
        )
>>>>>>> Stashed changes
    }
  } catch (error: any) {
    console.error('Error in integrated-quote GET:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ 
      error: 'Internal server error', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 })
=======
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Internal server error', 500, errorMessage)
>>>>>>> Stashed changes
  }
}
