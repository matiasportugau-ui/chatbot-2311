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
<<<<<<< Updated upstream
=======
import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'
>>>>>>> Stashed changes

type RouteContext = {
  params: {
    action: string
  }
}

<<<<<<< Updated upstream
function errorResponse(message: string, status: number = 400) {
  return NextResponse.json({ error: message }, { status })
}

export async function GET(request: NextRequest, context: RouteContext) {
  const action = context.params.action
=======
async function getOrdersHandler(request: NextRequest, context?: RouteContext) {
  // Extract action from URL path or context
>>>>>>> Stashed changes
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
    console.error(`Mercado Libre orders GET error (${action}):`, error)
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    return errorResponse(errorMessage, 500)
  }
}

<<<<<<< Updated upstream
export async function POST(request: NextRequest, context: RouteContext) {
  const action = context.params.action
=======
async function postOrdersHandler(request: NextRequest, context?: RouteContext) {
  // Extract action from URL path or context
  const url = new URL(request.url)
  const pathParts = url.pathname.split('/')
  const action = context?.params?.action || pathParts[pathParts.length - 1]
>>>>>>> Stashed changes
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
    console.error(`Mercado Libre orders POST error (${action}):`, error)
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    return errorResponse(errorMessage, 500)
  }
}

<<<<<<< Updated upstream
=======
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
>>>>>>> Stashed changes
