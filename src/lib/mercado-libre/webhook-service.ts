/**
 * Mercado Libre Webhook Service
 * Handles webhook events from Mercado Libre
 */

import * as crypto from 'crypto'
import { connectDB } from '../mongodb'

interface WebhookEvent {
  _id?: string
  topic: string
  resource: string
  user_id: number
  application_id: number
  attempts: number
  sent: string
  received: string
}

interface StoredWebhookEvent {
  event_id?: string
  topic: string
  resource: string
  user_id: number
  application_id: number
  attempts: number
  sent: string
  received: string
  processed: boolean
  processed_at?: Date
  error?: string
  received_at: Date
}

/**
 * Verify webhook signature from Mercado Libre
 * Uses HMAC SHA256 with the webhook secret
 */
export function verifyWebhookSignature(
  payload: string,
  signature: string | null
): boolean {
  const secret = process.env.MERCADO_LIBRE_WEBHOOK_SECRET

  // In development, allow unsigned webhooks
  if (process.env.NODE_ENV === 'development' && !secret) {
    console.warn('Webhook signature verification skipped in development')
    return true
  }

  if (!signature || !secret) {
    console.warn('Missing signature or webhook secret')
    return false
  }

  try {
    // Mercado Libre uses format: sha256=xxxxx
    const [algorithm, hash] = signature.split('=')
    if (algorithm !== 'sha256' || !hash) {
      return false
    }

    const expectedHash = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex')

    return crypto.timingSafeEqual(
      Buffer.from(hash),
      Buffer.from(expectedHash)
    )
  } catch (error) {
    console.error('Error verifying webhook signature:', error)
    return false
  }
}

/**
 * Process incoming webhook event
 * Stores the event and triggers appropriate handlers
 */
export async function processWebhookEvent(event: WebhookEvent): Promise<void> {
  const storedEvent: StoredWebhookEvent = {
    event_id: event._id,
    topic: event.topic,
    resource: event.resource,
    user_id: event.user_id,
    application_id: event.application_id,
    attempts: event.attempts,
    sent: event.sent,
    received: event.received,
    processed: false,
    received_at: new Date(),
  }

  // Store event in database
  try {
    const db = await connectDB()
    await db.collection('mercado_libre_webhooks').insertOne(storedEvent)
  } catch (error) {
    console.warn('Could not store webhook event:', error)
  }

  // Process event based on topic
  try {
    switch (event.topic) {
      case 'orders_v2':
        await handleOrderEvent(event)
        break
      case 'items':
        await handleItemEvent(event)
        break
      case 'questions':
        await handleQuestionEvent(event)
        break
      case 'payments':
        await handlePaymentEvent(event)
        break
      case 'shipments':
        await handleShipmentEvent(event)
        break
      default:
        console.log(`Unhandled webhook topic: ${event.topic}`)
    }

    // Mark as processed
    try {
      const db = await connectDB()
      await db.collection('mercado_libre_webhooks').updateOne(
        { event_id: event._id },
        {
          $set: {
            processed: true,
            processed_at: new Date(),
          },
        }
      )
    } catch {
      // Ignore update errors
    }
  } catch (error) {
    console.error(`Error processing webhook event (${event.topic}):`, error)
    
    // Store error
    try {
      const db = await connectDB()
      await db.collection('mercado_libre_webhooks').updateOne(
        { event_id: event._id },
        {
          $set: {
            error: error instanceof Error ? error.message : 'Unknown error',
          },
        }
      )
    } catch {
      // Ignore update errors
    }

    throw error
  }
}

/**
 * Handle order events
 */
async function handleOrderEvent(event: WebhookEvent): Promise<void> {
  const orderId = extractResourceId(event.resource)
  console.log(`Processing order event: ${orderId}`)

  // You could fetch the full order here and update your database
  // const order = await meliRequest(`/orders/${orderId}`)
  // await updateStoredOrder(order)
}

/**
 * Handle item/listing events
 */
async function handleItemEvent(event: WebhookEvent): Promise<void> {
  const itemId = extractResourceId(event.resource)
  console.log(`Processing item event: ${itemId}`)
}

/**
 * Handle question events
 */
async function handleQuestionEvent(event: WebhookEvent): Promise<void> {
  const questionId = extractResourceId(event.resource)
  console.log(`Processing question event: ${questionId}`)
}

/**
 * Handle payment events
 */
async function handlePaymentEvent(event: WebhookEvent): Promise<void> {
  const paymentId = extractResourceId(event.resource)
  console.log(`Processing payment event: ${paymentId}`)
}

/**
 * Handle shipment events
 */
async function handleShipmentEvent(event: WebhookEvent): Promise<void> {
  const shipmentId = extractResourceId(event.resource)
  console.log(`Processing shipment event: ${shipmentId}`)
}

/**
 * Extract resource ID from resource path
 * e.g., "/orders/123456" -> "123456"
 */
function extractResourceId(resource: string): string {
  const parts = resource.split('/')
  return parts[parts.length - 1]
}

/**
 * Get recent webhook events from database
 */
export async function getRecentWebhookEvents(
  limit: number = 50
): Promise<StoredWebhookEvent[]> {
  try {
    const db = await connectDB()
    const events = await db
      .collection('mercado_libre_webhooks')
      .find({})
      .sort({ received_at: -1 })
      .limit(limit)
      .toArray()

    return events as unknown as StoredWebhookEvent[]
  } catch (error) {
    console.warn('Could not fetch webhook events:', error)
    return []
  }
}

/**
 * Get unprocessed webhook events
 */
export async function getUnprocessedEvents(): Promise<StoredWebhookEvent[]> {
  try {
    const db = await connectDB()
    const events = await db
      .collection('mercado_libre_webhooks')
      .find({ processed: false })
      .sort({ received_at: 1 })
      .toArray()

    return events as unknown as StoredWebhookEvent[]
  } catch (error) {
    console.warn('Could not fetch unprocessed events:', error)
    return []
  }
}
