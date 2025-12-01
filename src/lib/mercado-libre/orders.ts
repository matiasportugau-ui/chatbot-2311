/**
 * Mercado Libre Orders Module
 * Handles order operations for Mercado Libre
 */

import { meliRequest } from './client'
import { connectDB } from '../mongodb'

interface OrderItem {
  item: {
    id: string
    title: string
    category_id: string
  }
  quantity: number
  unit_price: number
  full_unit_price: number
  currency_id: string
}

interface OrderBuyer {
  id: number
  nickname: string
  first_name?: string
  last_name?: string
  email?: string
  phone?: {
    area_code: string
    number: string
    extension?: string
  }
}

interface OrderShipping {
  id: number
  status: string
  date_created: string
  receiver_address?: {
    address_line: string
    city: { name: string }
    state: { name: string }
    zip_code: string
  }
}

interface Order {
  id: number
  status: string
  status_detail: string
  date_created: string
  date_closed?: string
  order_items: OrderItem[]
  buyer: OrderBuyer
  total_amount: number
  currency_id: string
  shipping?: OrderShipping
  payments?: Array<{
    id: number
    status: string
    transaction_amount: number
  }>
  feedback?: {
    sale?: { fulfilled: boolean }
    purchase?: { fulfilled: boolean }
  }
  tags?: string[]
}

interface OrdersSearchResponse {
  query: string
  results: Order[]
  paging: {
    total: number
    offset: number
    limit: number
  }
}

interface SyncOrdersParams {
  limit?: number
  status?: string
  dateFrom?: string
  dateTo?: string
}

interface OrdersSummary {
  total: number
  pending: number
  paid: number
  shipped: number
  delivered: number
  cancelled: number
  lastSync?: Date
}

/**
 * Sync orders from Mercado Libre API and store in database
 */
export async function syncSellerOrders(
  params: SyncOrdersParams = {}
): Promise<{ synced: number; total: number }> {
  const { limit = 50, status, dateFrom, dateTo } = params
  const sellerId = process.env.MERCADO_LIBRE_SELLER_ID

  if (!sellerId) {
    throw new Error('MERCADO_LIBRE_SELLER_ID is not configured')
  }

  // Build query
  const queryParams = new URLSearchParams({
    seller: sellerId,
    limit: limit.toString(),
    sort: 'date_desc',
  })

  if (status) {
    queryParams.set('order.status', status)
  }
  if (dateFrom) {
    queryParams.set('order.date_created.from', dateFrom)
  }
  if (dateTo) {
    queryParams.set('order.date_created.to', dateTo)
  }

  const response = await meliRequest<OrdersSearchResponse>(
    `/orders/search?${queryParams}`
  )

  // Store orders in database
  try {
    const db = await connectDB()
    const collection = db.collection('mercado_libre_orders')

    let synced = 0
    for (const order of response.results) {
      await collection.updateOne(
        { id: order.id },
        {
          $set: {
            ...order,
            synced_at: new Date(),
          },
        },
        { upsert: true }
      )
      synced++
    }

    // Update last sync time
    await db.collection('mercado_libre_sync').updateOne(
      { type: 'orders' },
      { $set: { last_sync: new Date(), count: response.paging.total } },
      { upsert: true }
    )

    return { synced, total: response.paging.total }
  } catch (error) {
    console.warn('Could not store orders in MongoDB:', error)
    return { synced: 0, total: response.paging.total }
  }
}

/**
 * Get stored orders from database
 */
export async function getStoredOrders(limit: number = 20): Promise<Order[]> {
  try {
    const db = await connectDB()
    const orders = await db
      .collection('mercado_libre_orders')
      .find({})
      .sort({ date_created: -1 })
      .limit(limit)
      .toArray()

    return orders as unknown as Order[]
  } catch (error) {
    console.warn('Could not fetch orders from MongoDB:', error)
    return []
  }
}

/**
 * Get orders summary statistics
 */
export async function getOrdersSummary(): Promise<OrdersSummary> {
  try {
    const db = await connectDB()
    const collection = db.collection('mercado_libre_orders')

    const [total, pending, paid, shipped, delivered, cancelled] =
      await Promise.all([
        collection.countDocuments({}),
        collection.countDocuments({ status: 'pending' }),
        collection.countDocuments({ status: 'paid' }),
        collection.countDocuments({ status: 'shipped' }),
        collection.countDocuments({ status: 'delivered' }),
        collection.countDocuments({ status: 'cancelled' }),
      ])

    // Get last sync time
    const syncInfo = await db
      .collection('mercado_libre_sync')
      .findOne({ type: 'orders' })

    return {
      total,
      pending,
      paid,
      shipped,
      delivered,
      cancelled,
      lastSync: syncInfo?.last_sync,
    }
  } catch (error) {
    console.warn('Could not fetch orders summary from MongoDB:', error)
    return {
      total: 0,
      pending: 0,
      paid: 0,
      shipped: 0,
      delivered: 0,
      cancelled: 0,
    }
  }
}

/**
 * Acknowledge an order (mark as seen/processed)
 */
export async function acknowledgeOrder(orderId: number): Promise<Order> {
  // Update the order notes/tags
  const order = await meliRequest<Order>(`/orders/${orderId}`)

  // Store acknowledgment in database
  try {
    const db = await connectDB()
    await db.collection('mercado_libre_orders').updateOne(
      { id: orderId },
      {
        $set: {
          acknowledged: true,
          acknowledged_at: new Date(),
        },
      }
    )
  } catch (error) {
    console.warn('Could not update order acknowledgment:', error)
  }

  return order
}

/**
 * Mark order as ready to ship
 */
export async function markOrderReadyToShip(
  orderId: number,
  trackingNumber?: string
): Promise<Order> {
  const order = await meliRequest<Order>(`/orders/${orderId}`)

  if (!order.shipping?.id) {
    throw new Error('Order does not have shipping information')
  }

  // If tracking number provided, update shipment
  if (trackingNumber) {
    await meliRequest(`/shipments/${order.shipping.id}`, {
      method: 'PUT',
      body: JSON.stringify({
        tracking_number: trackingNumber,
      }),
    })
  }

  // Update status in database
  try {
    const db = await connectDB()
    await db.collection('mercado_libre_orders').updateOne(
      { id: orderId },
      {
        $set: {
          ready_to_ship: true,
          ready_to_ship_at: new Date(),
          tracking_number: trackingNumber,
        },
      }
    )
  } catch (error) {
    console.warn('Could not update order status:', error)
  }

  return order
}

/**
 * Get single order by ID
 */
export async function getOrder(orderId: number): Promise<Order> {
  return meliRequest<Order>(`/orders/${orderId}`)
}
