import { NextRequest, NextResponse } from 'next/server'
import { GoogleSheetsEnhancedClient } from '@/lib/google-sheets-enhanced'
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
 * 📊 API de Sincronización Mejorada con Google Sheets
 * 
 * Endpoints para gestión completa del "Administrador de Cotizaciones"
 */

export async function GET(request: NextRequest) {
  try {
    await ensureSystemInitialized()
    
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action') || 'all'
    const phone = searchParams.get('phone')
    const arg = searchParams.get('arg')
    
    const sheetsClient = new GoogleSheetsEnhancedClient()
    
    switch (action) {
      case 'all':
        return await getAllData(sheetsClient)
      
      case 'admin':
        return await getAdminData(sheetsClient)
      
      case 'enviados':
        return await getEnviadosData(sheetsClient)
      
      case 'confirmados':
        return await getConfirmadosData(sheetsClient)
      
      case 'statistics':
        return await getStatistics(sheetsClient)
      
      case 'search':
        if (phone) {
          return await searchByPhone(sheetsClient, phone)
        } else if (arg) {
          return await searchByArg(sheetsClient, arg)
        } else {
          return NextResponse.json({ error: 'Missing phone or arg parameter' }, { status: 400 })
        }
      
      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
    }
  } catch (error: any) {
    console.error('Error in enhanced-sync GET:', error)
    return NextResponse.json({ 
      error: 'Internal server error', 
      details: error.message 
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    await ensureSystemInitialized()
    
    const body = await request.json()
    const { action, data } = body
    
    const sheetsClient = new GoogleSheetsEnhancedClient()
    
    switch (action) {
      case 'add_quote':
        return await addQuote(sheetsClient, data)
      
      case 'move_to_enviados':
        return await moveToEnviados(sheetsClient, data)
      
      case 'move_to_confirmado':
        return await moveToConfirmado(sheetsClient, data)
      
      case 'update_status':
        return await updateStatus(sheetsClient, data)
      
      case 'update_cell':
        return await updateCell(sheetsClient, data)
      
      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
    }
  } catch (error: any) {
    console.error('Error in enhanced-sync POST:', error)
    return NextResponse.json({ 
      error: 'Internal server error', 
      details: error.message 
    }, { status: 500 })
  }
}

/**
 * 📋 Obtener todos los datos
 */
async function getAllData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const [adminData, enviadosData, confirmadosData, statistics] = await Promise.all([
      sheetsClient.readAdminTab(),
      sheetsClient.readEnviadosTab(),
      sheetsClient.readConfirmadoTab(),
      sheetsClient.getStatistics()
    ])
    
    return NextResponse.json({
      success: true,
      data: {
        admin: adminData,
        enviados: enviadosData,
        confirmados: confirmadosData,
        statistics,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error getting all data: ${error.message}`)
  }
}

/**
 * 📋 Obtener datos de Admin
 */
async function getAdminData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const adminData = await sheetsClient.readAdminTab()
    
    return NextResponse.json({
      success: true,
      data: {
        admin: adminData,
        count: adminData.length,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error getting admin data: ${error.message}`)
  }
}

/**
 * 📤 Obtener datos de Enviados
 */
async function getEnviadosData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const enviadosData = await sheetsClient.readEnviadosTab()
    
    return NextResponse.json({
      success: true,
      data: {
        enviados: enviadosData,
        count: enviadosData.length,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error getting enviados data: ${error.message}`)
  }
}

/**
 * ✅ Obtener datos de Confirmados
 */
async function getConfirmadosData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const confirmadosData = await sheetsClient.readConfirmadoTab()
    
    return NextResponse.json({
      success: true,
      data: {
        confirmados: confirmadosData,
        count: confirmadosData.length,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error getting confirmados data: ${error.message}`)
  }
}

/**
 * 📊 Obtener estadísticas
 */
async function getStatistics(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const statistics = await sheetsClient.getStatistics()
    
    return NextResponse.json({
      success: true,
      data: {
        statistics,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error getting statistics: ${error.message}`)
  }
}

/**
 * 🔍 Buscar por teléfono
 */
async function searchByPhone(sheetsClient: GoogleSheetsEnhancedClient, phone: string) {
  try {
    const results = await sheetsClient.findByPhone(phone)
    
    return NextResponse.json({
      success: true,
      data: {
        phone,
        results,
        total: results.pendientes.length + results.enviados.length + results.confirmados.length,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error searching by phone: ${error.message}`)
  }
}

/**
 * 🔍 Buscar por código Arg
 */
async function searchByArg(sheetsClient: GoogleSheetsEnhancedClient, arg: string) {
  try {
    const results = await sheetsClient.findByArg(arg)
    
    return NextResponse.json({
      success: true,
      data: {
        arg,
        results,
        found: !!(results.admin || results.enviados || results.confirmados),
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error searching by arg: ${error.message}`)
  }
}

/**
 * ➕ Agregar cotización
 */
async function addQuote(sheetsClient: GoogleSheetsEnhancedClient, data: any) {
  try {
    // Generar código Arg si no se proporciona
    if (!data.arg) {
      data.arg = sheetsClient.generateArgCode(data.telefono, data.origen || 'WA')
    }
    
    await sheetsClient.addQuoteToAdmin(data)
    
    return NextResponse.json({
      success: true,
      data: {
        message: 'Cotización agregada exitosamente',
        arg: data.arg,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error adding quote: ${error.message}`)
  }
}

/**
 * 📤 Mover a Enviados
 */
async function moveToEnviados(sheetsClient: GoogleSheetsEnhancedClient, data: any) {
  try {
    await sheetsClient.moveToEnviados(data.rowNumber, data.additionalData)
    
    return NextResponse.json({
      success: true,
      data: {
        message: 'Cotización movida a Enviados exitosamente',
        rowNumber: data.rowNumber,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error moving to enviados: ${error.message}`)
  }
}

/**
 * ✅ Mover a Confirmado
 */
async function moveToConfirmado(sheetsClient: GoogleSheetsEnhancedClient, data: any) {
  try {
    await sheetsClient.moveToConfirmado(data.rowNumber, data.additionalData)
    
    return NextResponse.json({
      success: true,
      data: {
        message: 'Cotización movida a Confirmado exitosamente',
        rowNumber: data.rowNumber,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error moving to confirmado: ${error.message}`)
  }
}

/**
 * 🔄 Actualizar estado
 */
async function updateStatus(sheetsClient: GoogleSheetsEnhancedClient, data: any) {
  try {
    await sheetsClient.updateCellValue(data.sheetName, data.row, 'B', data.status)
    
    return NextResponse.json({
      success: true,
      data: {
        message: 'Estado actualizado exitosamente',
        sheetName: data.sheetName,
        row: data.row,
        status: data.status,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error updating status: ${error.message}`)
  }
}

/**
 * 🔧 Actualizar celda específica
 */
async function updateCell(sheetsClient: GoogleSheetsEnhancedClient, data: any) {
  try {
    await sheetsClient.updateCellValue(data.sheetName, data.row, data.column, data.value)
    
    return NextResponse.json({
      success: true,
      data: {
        message: 'Celda actualizada exitosamente',
        sheetName: data.sheetName,
        row: data.row,
        column: data.column,
        value: data.value,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error: any) {
    throw new Error(`Error updating cell: ${error.message}`)
  }
}
