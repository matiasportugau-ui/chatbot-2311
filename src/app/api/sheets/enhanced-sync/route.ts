export const dynamic = 'force-dynamic'

import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import {
  GoogleSheetsEnhancedClient,
  QuoteData,
} from '@/lib/google-sheets-enhanced'
import { initializeBMCSystem } from '@/lib/initialize-system'

import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'


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
          return validationErrorResponse(
            ['Missing phone or arg parameter'],
            'Search requires phone or arg parameter'
          )
        }

      default:
        return validationErrorResponse(
          ['Invalid action'],
          'Invalid action parameter'
        )
    }
  } catch (error: any) {
    console.error('Error in enhanced-sync GET:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Internal server error', 500, errorMessage)
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
        return validationErrorResponse(
          ['Invalid action'],
          'Invalid action parameter'
        )
    }
  } catch (error: any) {
    console.error('Error in enhanced-sync POST:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse('Internal server error', 500, errorMessage)
  }
}

/**
 * 📋 Obtener todos los datos
 */
async function getAllData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const [adminData, enviadosData, confirmadosData, statistics] =
      await Promise.all([
        sheetsClient.readAdminTab(),
        sheetsClient.readEnviadosTab(),
        sheetsClient.readConfirmadoTab(),
        sheetsClient.getStatistics(),
      ])

    return successResponse({
      admin: adminData,
      enviados: enviadosData,
      confirmados: confirmadosData,
      statistics,
      timestamp: new Date().toISOString(),
    })

  } catch (error: unknown) {
    throw new Error(
      `Error getting all data: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 📋 Obtener datos de Admin
 */
async function getAdminData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const adminData = await sheetsClient.readAdminTab()

    return successResponse({
      admin: adminData,
      count: adminData.length,
      timestamp: new Date().toISOString(),
    })

  } catch (error: unknown) {
    throw new Error(
      `Error getting admin data: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 📤 Obtener datos de Enviados
 */
async function getEnviadosData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const enviadosData = await sheetsClient.readEnviadosTab()

    return successResponse({
      enviados: enviadosData,
      count: enviadosData.length,
      timestamp: new Date().toISOString(),
    })

  } catch (error: unknown) {
    throw new Error(
      `Error getting enviados data: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * ✅ Obtener datos de Confirmados
 */
async function getConfirmadosData(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const confirmadosData = await sheetsClient.readConfirmadoTab()

    return successResponse({
      confirmados: confirmadosData,
      count: confirmadosData.length,
      timestamp: new Date().toISOString(),
    })

  } catch (error: unknown) {
    throw new Error(
      `Error getting confirmados data: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 📊 Obtener estadísticas
 */
async function getStatistics(sheetsClient: GoogleSheetsEnhancedClient) {
  try {
    const statistics = await sheetsClient.getStatistics()

    return successResponse({
      statistics,
      timestamp: new Date().toISOString(),
    })

  } catch (error: unknown) {
    throw new Error(
      `Error getting statistics: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 🔍 Buscar por teléfono
 */
async function searchByPhone(
  sheetsClient: GoogleSheetsEnhancedClient,
  phone: string
) {
  try {
    const results = await sheetsClient.findByPhone(phone)

    return successResponse({
      phone,
      results,
      total:
        results.pendientes.length +
        results.enviados.length +
        results.confirmados.length,
      timestamp: new Date().toISOString(),
    })

  } catch (error: unknown) {
    throw new Error(
      `Error searching by phone: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 🔍 Buscar por código Arg
 */
async function searchByArg(
  sheetsClient: GoogleSheetsEnhancedClient,
  arg: string
) {
  try {
    const results = await sheetsClient.findByArg(arg)

    return successResponse({
      arg,
      results,
      found: !!(results.admin || results.enviados || results.confirmados),
      timestamp: new Date().toISOString(),
    })

  } catch (error: unknown) {
    throw new Error(
      `Error searching by arg: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * ➕ Agregar cotización
 */

async function addQuote(
  sheetsClient: GoogleSheetsEnhancedClient,
  data: Record<string, unknown>
) {

  try {
    // Convert data to QuoteData format
    const quoteData: QuoteData = {
      arg: typeof data.arg === 'string' ? data.arg : '',
      estado: typeof data.estado === 'string' ? data.estado : 'Pendiente',
      fecha:
        typeof data.fecha === 'string'
          ? data.fecha
          : new Date().toISOString().split('T')[0],
      cliente: typeof data.cliente === 'string' ? data.cliente : '',
      origen: typeof data.origen === 'string' ? data.origen : 'WA',
      telefono:
        typeof data.telefono === 'string'
          ? data.telefono
          : String(data.telefono || ''),
      direccion: typeof data.direccion === 'string' ? data.direccion : '',
      consulta: typeof data.consulta === 'string' ? data.consulta : '',
      precio: typeof data.precio === 'string' ? data.precio : undefined,
      fechaEnvio:
        typeof data.fechaEnvio === 'string' ? data.fechaEnvio : undefined,
    }

    // Generar código Arg si no se proporciona
    if (!quoteData.arg) {
      quoteData.arg = await sheetsClient.generateArgCode(
        quoteData.telefono,
        quoteData.origen
      )
    }

    await sheetsClient.addQuoteToAdmin(quoteData)

    return successResponse(
      {
        message: 'Cotización agregada exitosamente',

        arg: quoteData.arg,
        timestamp: new Date().toISOString(),
      },
      'Cotización agregada exitosamente'
    )
  } catch (error: unknown) {
    throw new Error(
      `Error adding quote: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 📤 Mover a Enviados
 */

async function moveToEnviados(
  sheetsClient: GoogleSheetsEnhancedClient,
  data: Record<string, unknown>
) {

  try {
    const rowNumber =
      typeof data.rowNumber === 'number'
        ? data.rowNumber
        : Number(data.rowNumber)
    if (Number.isNaN(rowNumber) || rowNumber <= 0) {
      throw new Error('rowNumber must be a positive number')
    }
    await sheetsClient.moveToEnviados(rowNumber, data.additionalData)

    return successResponse(
      {
        message: 'Cotización movida a Enviados exitosamente',

        rowNumber,
        timestamp: new Date().toISOString(),
      },
      'Cotización movida a Enviados exitosamente'
    )
  } catch (error: unknown) {
    throw new Error(
      `Error moving to enviados: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * ✅ Mover a Confirmado
 */

async function moveToConfirmado(
  sheetsClient: GoogleSheetsEnhancedClient,
  data: Record<string, unknown>
) {

  try {
    const rowNumber =
      typeof data.rowNumber === 'number'
        ? data.rowNumber
        : Number(data.rowNumber)
    if (Number.isNaN(rowNumber) || rowNumber <= 0) {
      throw new Error('rowNumber must be a positive number')
    }
    await sheetsClient.moveToConfirmado(rowNumber, data.additionalData)

    return successResponse(
      {
        message: 'Cotización movida a Confirmado exitosamente',

        rowNumber,
        timestamp: new Date().toISOString(),
      },
      'Cotización movida a Confirmado exitosamente'
    )
  } catch (error: unknown) {
    throw new Error(
      `Error moving to confirmado: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 🔄 Actualizar estado
 */

async function updateStatus(
  sheetsClient: GoogleSheetsEnhancedClient,
  data: Record<string, unknown>
) {

  try {
    const sheetName =
      typeof data.sheetName === 'string'
        ? data.sheetName
        : String(data.sheetName || '')
    const row = typeof data.row === 'number' ? data.row : Number(data.row)
    const status =
      typeof data.status === 'string' ? data.status : String(data.status || '')

    if (!sheetName) {
      throw new Error('sheetName is required')
    }
    if (Number.isNaN(row) || row <= 0) {
      throw new Error('row must be a positive number')
    }

    await sheetsClient.updateCellValue(sheetName, row, 'B', status)

    return successResponse(
      {
        message: 'Estado actualizado exitosamente',

        sheetName,
        row,
        status,
        timestamp: new Date().toISOString(),
      },
      'Estado actualizado exitosamente'
    )
  } catch (error: unknown) {
    throw new Error(
      `Error updating status: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}

/**
 * 🔧 Actualizar celda específica
 */
interface UpdateCellData {
  sheetName: string
  row: number
  column: string
  value: unknown
}

async function updateCell(
  sheetsClient: GoogleSheetsEnhancedClient,
  data: UpdateCellData
) {
  try {
    const value =
      typeof data.value === 'string' ? data.value : String(data.value ?? '')
    await sheetsClient.updateCellValue(
      data.sheetName,
      data.row,
      data.column,
      value
    )

    return successResponse(
      {
        message: 'Celda actualizada exitosamente',
        sheetName: data.sheetName,
        row: data.row,
        column: data.column,
        value: data.value,

        timestamp: new Date().toISOString(),
      },
      'Celda actualizada exitosamente'
    )
  } catch (error: unknown) {
    throw new Error(
      `Error updating cell: ${error instanceof Error ? error.message : String(error)}`
    )

  }
}
