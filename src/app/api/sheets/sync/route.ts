import { NextRequest, NextResponse } from 'next/server'
import { GoogleSheetsClient } from '@/lib/google-sheets'

const sheetsClient = new GoogleSheetsClient()

export async function GET(request: NextRequest) {
  try {
    // Leer todas las cotizaciones de todas las pestañas
    const [adminData, enviadosData, confirmadosData, stats] = await Promise.all([
      sheetsClient.readAdminTab(),
      sheetsClient.readEnviadosTab(),
      sheetsClient.readConfirmadoTab(),
      sheetsClient.getStats()
    ])
    
    return NextResponse.json({
      success: true,
      data: {
        pendientes: adminData,
        enviados: enviadosData,
        confirmados: confirmadosData,
        stats: stats
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error in sheets sync GET:', error)
    return NextResponse.json({ 
      success: false,
      error: error.message 
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, data } = body
    
    switch (action) {
      case 'add_quote':
        await sheetsClient.addQuoteToAdmin(data)
        return NextResponse.json({ 
          success: true, 
          message: 'Quote added to Admin tab successfully' 
        })
        
      case 'move_to_enviados':
        await sheetsClient.moveToEnviados(data.rowNumber, data.additionalData)
        return NextResponse.json({ 
          success: true, 
          message: 'Quote moved to Enviados tab successfully' 
        })
        
      case 'move_to_confirmado':
        await sheetsClient.moveToConfirmado(data.rowNumber)
        return NextResponse.json({ 
          success: true, 
          message: 'Quote moved to Confirmado tab successfully' 
        })
        
      case 'update_status':
        await sheetsClient.updateCellValue(data.sheetName, data.row, data.column, data.status)
        return NextResponse.json({ 
          success: true, 
          message: 'Status updated successfully' 
        })
        
      case 'find_by_phone':
        const phoneResults = await sheetsClient.findByPhone(data.phone)
        return NextResponse.json({ 
          success: true, 
          data: phoneResults 
        })
        
      case 'get_stats':
        const stats = await sheetsClient.getStats()
        return NextResponse.json({ 
          success: true, 
          data: stats 
        })
        
      default:
        return NextResponse.json({ 
          success: false,
          error: 'Invalid action. Supported actions: add_quote, move_to_enviados, move_to_confirmado, update_status, find_by_phone, get_stats' 
        }, { status: 400 })
    }
  } catch (error) {
    console.error('Error in sheets sync POST:', error)
    return NextResponse.json({ 
      success: false,
      error: error.message 
    }, { status: 500 })
  }
}
