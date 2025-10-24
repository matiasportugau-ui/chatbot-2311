import { NextRequest, NextResponse } from 'next/server'
import { motorCotizacionIntegrado } from '@/lib/integrated-quote-engine'
import { initializeBMCSystem } from '@/lib/initialize-system'

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
      return NextResponse.json({ 
        error: 'Missing required parameters: consulta, userPhone' 
      }, { status: 400 })
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
        return NextResponse.json({ 
          error: 'Invalid action. Use: process, metrics, update_knowledge, analyze_patterns' 
        }, { status: 400 })
    }
  } catch (error: any) {
    console.error('Error in integrated-quote API:', error)
    return NextResponse.json({ 
      error: 'Internal server error', 
      details: error.message 
    }, { status: 500 })
  }
}

/**
 * 🔄 Procesar Consulta con IA Integrada
 */
async function procesarConsulta(consulta: string, userPhone: string, userName?: string) {
  try {
    const respuesta = await motorCotizacionIntegrado.procesarConsulta(
      consulta, 
      userPhone, 
      userName
    )
    
    return NextResponse.json({
      success: true,
      data: {
        respuesta,
        timestamp: new Date().toISOString(),
        session_id: `sess_${Date.now()}`,
        user_phone: userPhone
      }
    })
  } catch (error: any) {
    console.error('Error procesando consulta:', error)
    return NextResponse.json({ 
      error: 'Error procesando consulta', 
      details: error.message 
    }, { status: 500 })
  }
}

/**
 * 📊 Obtener Métricas del Sistema
 */
async function obtenerMetricas() {
  try {
    const metricas = await motorCotizacionIntegrado.obtenerMetricas()
    
    return NextResponse.json({
      success: true,
      data: {
        metricas,
        timestamp: new Date().toISOString(),
        status: 'active'
      }
    })
  } catch (error: any) {
    console.error('Error obteniendo métricas:', error)
    return NextResponse.json({ 
      error: 'Error obteniendo métricas', 
      details: error.message 
    }, { status: 500 })
  }
}

/**
 * 🧠 Actualizar Base de Conocimiento
 */
async function actualizarBaseConocimiento() {
  try {
    await motorCotizacionIntegrado.actualizarBaseConocimiento()
    
    return NextResponse.json({
      success: true,
      message: 'Base de conocimiento actualizada correctamente',
      timestamp: new Date().toISOString()
    })
  } catch (error: any) {
    console.error('Error actualizando base de conocimiento:', error)
    return NextResponse.json({ 
      error: 'Error actualizando base de conocimiento', 
      details: error.message 
    }, { status: 500 })
  }
}

/**
 * 🔍 Analizar Patrones de Venta
 */
async function analizarPatrones() {
  try {
    // Esta función podría implementar análisis más avanzados
    const metricas = await motorCotizacionIntegrado.obtenerMetricas()
    
    return NextResponse.json({
      success: true,
      data: {
        patrones_identificados: metricas.patrones_identificados,
        productos_mas_consultados: 'Análisis en desarrollo',
        zonas_mas_activas: 'Análisis en desarrollo',
        horarios_pico: 'Análisis en desarrollo',
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    console.error('Error analizando patrones:', error)
    return NextResponse.json({ 
      error: 'Error analizando patrones', 
      details: error.message 
    }, { status: 500 })
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
        })
      
      case 'health':
        return NextResponse.json({
          success: true,
          data: {
            status: 'healthy',
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            timestamp: new Date().toISOString()
          }
        })
      
      default:
        return NextResponse.json({ 
          error: 'Invalid action. Use: info, health' 
        }, { status: 400 })
    }
  } catch (error: any) {
    console.error('Error in integrated-quote GET:', error)
    return NextResponse.json({ 
      error: 'Internal server error', 
      details: error.message 
    }, { status: 500 })
  }
}
