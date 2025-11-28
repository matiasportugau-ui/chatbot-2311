import { NextRequest, NextResponse } from 'next/server'
import {
  acknowledgeOrder,
  getOrdersSummary,
  getStoredOrders,
  markOrderReadyToShip,
  syncSellerOrders
} from '@/lib/mercado-libre/orders'

type RouteContext = {
  params: {
    action: string
  }
}

function errorResponse(message: string, status: number = 400) {
  return NextResponse.json({ error: message }, { status })
}

export async function GET(request: NextRequest, context: RouteContext) {
  const action = context.params.action
  const url = new URL(request.url)

  try {
    if (action === 'list') {
      const limit = Number(url.searchParams.get('limit') || '20')
      const orders = await getStoredOrders(limit)
      return NextResponse.json({ orders })
    }

    if (action === 'summary') {
      const summary = await getOrdersSummary()
      return NextResponse.json(summary)
    }

    return errorResponse(`Acción no soportada: ${action}`)
  } catch (error) {
    console.error(`Mercado Libre orders GET error (${action}):`, error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error desconocido' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const action = context.params.action
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
      return NextResponse.json(result)
    }

    if (action === 'acknowledge') {
      const { orderId } = body
      if (!orderId) {
        return errorResponse('orderId es obligatorio')
      }
      const order = await acknowledgeOrder(Number(orderId))
      return NextResponse.json({ order, acknowledged: true })
    }

    if (action === 'ship') {
      const { orderId, trackingNumber } = body
      if (!orderId) {
        return errorResponse('orderId es obligatorio')
      }
      const order = await markOrderReadyToShip(Number(orderId), trackingNumber)
      return NextResponse.json({ order, readyToShip: true })
    }

    return errorResponse(`Acción no soportada: ${action}`)
  } catch (error) {
    console.error(`Mercado Libre orders POST error (${action}):`, error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error desconocido' },
      { status: 500 }
    )
  }
}

