import { NextRequest, NextResponse } from 'next/server'
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import {
  acknowledgeOrder,
  getOrdersSummary,
  getStoredOrders,
  markOrderReadyToShip,
  syncSellerOrders
} from '@/lib/mercado-libre/orders'

import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'


type RouteContext = {
  params: {
    action: string
  }
}


async function getOrdersHandler(request: NextRequest, context?: RouteContext) {
  // Extract action from URL path or context

  const url = new URL(request.url)
  const pathParts = url.pathname.split('/')
  const action = context?.params?.action || pathParts[pathParts.length - 1]

  try {
    if (action === 'list') {
      let limit = Number(url.searchParams.get('limit') || '20')
      // Validate limit to prevent NaN
      if (Number.isNaN(limit) || limit <= 0) {
        limit = 20 // Use default if invalid
      }
      const orders = await getStoredOrders(limit)
      return successResponse({ orders })
    }

    if (action === 'summary') {
      const summary = await getOrdersSummary()
      return successResponse(summary)
    }

    return validationErrorResponse(
      [`Acción no soportada: ${action}`],
      'Invalid action'
    )
  } catch (error: unknown) {
    const errorContext = {
      action,
      method: 'GET',
      url: request.url,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      details: (error as any)?.details,
    }
    
    console.error(
      `[MercadoLibre Orders] Error en GET ${action}:`,
      JSON.stringify(errorContext, null, 2)
    )
    
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    
    // Determinar código de estado apropiado
    let statusCode = 500
    if ((error as any)?.details?.error === 'invalid_grant') {
      statusCode = 401
    } else if (error instanceof Error && error.message.includes('no está conectado')) {
      statusCode = 401
    }
    
    return errorResponse(errorMessage, statusCode)
  }
}


async function postOrdersHandler(request: NextRequest, context?: RouteContext) {
  // Extract action from URL path or context
  const url = new URL(request.url)
  const pathParts = url.pathname.split('/')
  const action = context?.params?.action || pathParts[pathParts.length - 1]

  const body = await request.json().catch(() => ({}))

  try {
    if (action === 'sync') {
      const params = {
        limit: body.limit,
        status: body.status,
        dateFrom: body.dateFrom,
        dateTo: body.dateTo
      }
      const result = await syncSellerOrders(params)
      return successResponse(result)
    }

    if (action === 'acknowledge') {
      const { orderId } = body
      if (!orderId) {
        return validationErrorResponse(
          ['orderId es obligatorio'],
          'Missing required field'
        )
      }
      const parsedOrderId = Number(orderId)
      if (Number.isNaN(parsedOrderId)) {
        return validationErrorResponse(
          ['orderId debe ser un número válido'],
          'Invalid orderId format'
        )
      }
      const order = await acknowledgeOrder(parsedOrderId)
      return successResponse({ order, acknowledged: true })
    }

    if (action === 'ship') {
      const { orderId, trackingNumber } = body
      if (!orderId) {
        return validationErrorResponse(
          ['orderId es obligatorio'],
          'Missing required field'
        )
      }
      const parsedOrderId = Number(orderId)
      if (Number.isNaN(parsedOrderId)) {
        return validationErrorResponse(
          ['orderId debe ser un número válido'],
          'Invalid orderId format'
        )
      }
      const order = await markOrderReadyToShip(parsedOrderId, trackingNumber)
      return successResponse({ order, readyToShip: true })
    }

    return validationErrorResponse(
      [`Acción no soportada: ${action}`],
      'Invalid action'
    )
  } catch (error: unknown) {
    const errorContext = {
      action,
      method: 'POST',
      url: request.url,
      body: body,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      details: (error as any)?.details,
    }
    
    console.error(
      `[MercadoLibre Orders] Error en POST ${action}:`,
      JSON.stringify(errorContext, null, 2)
    )
    
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    
    // Determinar código de estado apropiado
    let statusCode = 500
    if ((error as any)?.details?.error === 'invalid_grant') {
      statusCode = 401
    } else if (error instanceof Error && error.message.includes('no está conectado')) {
      statusCode = 401
    } else if (error instanceof Error && error.message.includes('obligatorio')) {
      statusCode = 400
    }
    
    return errorResponse(errorMessage, statusCode)
  }
}


// Wrapper functions that extract action from URL for rate limiting compatibility
async function getHandlerWrapper(request: NextRequest) {
  const url = new URL(request.url)
  const pathParts = url.pathname.split('/')
  const action = pathParts[pathParts.length - 1]
  const context: RouteContext = { params: { action } }
  return getOrdersHandler(request, context)
}

async function postHandlerWrapper(request: NextRequest) {
  const url = new URL(request.url)
  const pathParts = url.pathname.split('/')
  const action = pathParts[pathParts.length - 1]
  const context: RouteContext = { params: { action } }
  return postOrdersHandler(request, context)
}

// Export with rate limiting
export const GET = withRateLimit(
  getHandlerWrapper,
  RATE_LIMITS.MERCADO_LIBRE.maxRequests,
  RATE_LIMITS.MERCADO_LIBRE.windowMs
)

export const POST = withRateLimit(
  postHandlerWrapper,
  RATE_LIMITS.MERCADO_LIBRE.maxRequests,
  RATE_LIMITS.MERCADO_LIBRE.windowMs
)

