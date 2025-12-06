import { connectDB } from '@/lib/mongodb'
import { MercadoLibreOrderRecord } from '@/models/Order'
import { callMercadoLibreAPI, getMercadoLibreConfig } from './client'
import { MercadoLibreOrder } from './types'

const COLLECTION = 'mercado_libre_orders'

export interface OrderSyncParams {
  limit?: number
  offset?: number
  status?: string
  dateFrom?: string
  dateTo?: string
}

export interface OrdersSummary {
  total: number
  pending: number
  paid: number
  delivered: number
  canceled: number
  totalRevenue: number
  currency: string
}

function normalizeOrder(order: MercadoLibreOrder): Omit<MercadoLibreOrderRecord, '_id' | 'createdAt'> {
  return {
    orderId: order.id,
    status: order.status,
    dateCreated: order.date_created,
    lastUpdated: order.date_last_updated || order.date_created,
    totalAmount: order.total_amount,
    currencyId: order.currency_id,
    buyer: {
      id: order.buyer?.id,
      nickname: order.buyer?.nickname,
      full_name: order.buyer?.first_name
        ? `${order.buyer?.first_name} ${order.buyer?.last_name || ''}`.trim()
        : order.buyer?.nickname,
      email: order.buyer?.email,
      phone: order.buyer?.phone?.number
    },
    payments: (order.payments || []).map((payment: any) => ({
      id: payment.id,
      status: payment.status,
      transaction_amount: payment.transaction_amount,
      method: payment.payment_method_id
    })),
    shipping: {
      status: order.shipping?.status,
      tracking_number: order.shipping?.tracking_number,
      mode: order.shipping?.shipping_mode
    },
    acknowledged: order.tags?.includes('paid') || false,
    readyToShip: order.shipping?.status === 'ready_to_ship',
    tags: order.tags || [],
    lastSync: new Date(),
    updatedAt: new Date()
  }
}

export async function syncSellerOrders(params: OrderSyncParams = {}) {
  const config = getMercadoLibreConfig()
  const query: Record<string, string> = {
    seller: config.sellerId,
    sort: 'date_desc',
    limit: String(params.limit ?? 20),
    offset: String(params.offset ?? 0)
  }

  if (params.status) {
    query['order.status'] = params.status
  }

  if (params.dateFrom) {
    query['order.date_created.from'] = params.dateFrom
  }

  if (params.dateTo) {
    query['order.date_created.to'] = params.dateTo
  }

  const response = await callMercadoLibreAPI<{
    results: MercadoLibreOrder[]
    paging: { total: number; limit: number; offset: number }
  }>({
    path: '/orders/search',
    query
  })

  const db = await connectDB()
  const collection = db.collection<MercadoLibreOrderRecord>(COLLECTION)
  const syncedOrders: MercadoLibreOrderRecord[] = []
  const now = new Date()

  for (const order of response.results || []) {
    const normalized = normalizeOrder(order)
    await collection.updateOne(
      { orderId: normalized.orderId },
      {
        $set: {
          ...normalized,
          updatedAt: now,
          lastSync: now
        },
        $setOnInsert: {
          createdAt: now,
          acknowledged: normalized.acknowledged
        }
      },
      { upsert: true }
    )
    syncedOrders.push({
      ...normalized,
      createdAt: now
    })
  }

  return {
    paging: response.paging,
    orders: syncedOrders
  }
}

export async function syncOrderById(orderId: number) {
  if (!orderId) {
    throw new Error('orderId es obligatorio')
  }

  const order = await callMercadoLibreAPI<MercadoLibreOrder>({
    path: `/orders/${orderId}`
  })

  const normalized = normalizeOrder(order)
  const db = await connectDB()
  const collection = db.collection<MercadoLibreOrderRecord>(COLLECTION)
  const now = new Date()

  await collection.updateOne(
    { orderId: normalized.orderId },
    {
      $set: {
        ...normalized,
        updatedAt: now,
        lastSync: now
      },
      $setOnInsert: {
        createdAt: now,
        acknowledged: normalized.acknowledged
      }
    },
    { upsert: true }
  )

  return collection.findOne({ orderId })
}

export async function getStoredOrders(limit: number = 20) {
  const db = await connectDB()
  const collection = db.collection<MercadoLibreOrderRecord>(COLLECTION)
  const orders = await collection.find({}).sort({ dateCreated: -1 }).limit(limit).toArray()
  return orders
}

export async function acknowledgeOrder(orderId: number) {
  const db = await connectDB()
  const collection = db.collection<MercadoLibreOrderRecord>(COLLECTION)
  await collection.updateOne(
    { orderId },
    {
      $set: {
        acknowledged: true,
        updatedAt: new Date()
      }
    }
  )
  return collection.findOne({ orderId })
}

export async function markOrderReadyToShip(orderId: number, trackingNumber?: string) {
  const db = await connectDB()
  const collection = db.collection<MercadoLibreOrderRecord>(COLLECTION)
  await collection.updateOne(
    { orderId },
    {
      $set: {
        readyToShip: true,
        'shipping.tracking_number': trackingNumber,
        updatedAt: new Date()
      }
    }
  )
  return collection.findOne({ orderId })
}

export async function getOrdersSummary(limit: number = 50): Promise<OrdersSummary> {
  const orders = await getStoredOrders(limit)
  const summary = orders.reduce(
    (acc, order) => {
      acc.total += 1
      acc.totalRevenue += order.totalAmount

      switch (order.status) {
        case 'paid':
          acc.paid += 1
          break
        case 'canceled':
          acc.canceled += 1
          break
        case 'delivered':
          acc.delivered += 1
          break
        default:
          acc.pending += 1
      }

      if (!acc.currency) {
        acc.currency = order.currencyId
      }

      return acc
    },
    {
      total: 0,
      pending: 0,
      paid: 0,
      delivered: 0,
      canceled: 0,
      totalRevenue: 0,
      currency: 'USD'
    } as OrdersSummary
  )

  return summary
}

