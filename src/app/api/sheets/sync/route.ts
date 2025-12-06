export const dynamic = 'force-dynamic';


import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { GoogleSheetsClient } from '@/lib/google-sheets'
import { NextRequest } from 'next/server'


export async function GET(request: NextRequest) {
  try {
    const sheetsClient = new GoogleSheetsClient()
    
    // Leer todas las cotizaciones de todas las pestañas

    const [adminData, enviadosData, confirmadosData, stats] = await Promise.all(
      [
        sheetsClient.readAdminTab(),
        sheetsClient.readEnviadosTab(),
        sheetsClient.readConfirmadoTab(),
        sheetsClient.getStats(),
      ]
    )

    return successResponse({
      pendientes: adminData,
      enviados: enviadosData,
      confirmados: confirmadosData,
      stats,

    })
  } catch (error: unknown) {
    console.error('Error in sheets sync:', error)

    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)

  }
}

export async function POST(request: NextRequest) {
  try {
    const sheetsClient = new GoogleSheetsClient()
    const body = await request.json()
    const { action, data } = body
    
    switch (action) {
      case 'add_quote':
        await sheetsClient.addQuoteToAdmin(data)

        return successResponse(null, 'Quote added to Admin tab successfully')

      case 'move_to_enviados':
        await sheetsClient.moveToEnviados(data.rowNumber, data.additionalData)
        return successResponse(null, 'Quote moved to Enviados tab successfully')

      case 'move_to_confirmado':
        await sheetsClient.moveToConfirmado(data.rowNumber)
        return successResponse(
          null,
          'Quote moved to Confirmado tab successfully'
        )

      case 'update_status':
        await sheetsClient.updateCellValue(
          data.sheetName,
          data.row,
          data.column,
          data.status
        )
        return successResponse(null, 'Status updated successfully')

      case 'find_by_phone':
        const phoneResults = await sheetsClient.findByPhone(data.phone)
        return successResponse(phoneResults)

      case 'get_stats':
        const stats = await sheetsClient.getStats()
        return successResponse(stats)

      default:
        return validationErrorResponse(
          [
            'Invalid action. Supported actions: add_quote, move_to_enviados, move_to_confirmado, update_status, find_by_phone, get_stats',
          ],
          'Invalid action parameter'
        )

    }
  } catch (error: unknown) {
    console.error('Error in sheets sync POST:', error)

    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)

  }
}
