import crypto from 'crypto'
import { connectDB } from '@/lib/mongodb'
import { syncOrderById } from './orders'

const COLLECTION = 'mercado_libre_webhook_events'

export function verifyWebhookSignature(rawBody: string, signatureHeader: string | null): boolean {
  const secret = process.env.MERCADO_LIBRE_WEBHOOK_SECRET
  if (!secret) {
    console.warn('Mercado Libre webhook secret not configured. Skipping signature validation.')
    return true
  }

  if (!signatureHeader) {
    return false
  }

  const [algo, signature] = signatureHeader.split('=')
  if (!algo || !signature) {
    return false
  }

  const hmac = crypto.createHmac(algo as any, secret)
  hmac.update(rawBody, 'utf8')
  const expected = hmac.digest('hex')
  const received = Buffer.from(signature)
  const expectedBuffer = Buffer.from(expected)

  if (received.length !== expectedBuffer.length) {
    return false
  }

  return crypto.timingSafeEqual(received, expectedBuffer)
}

export async function storeWebhookEvent(event: any) {
  const db = await connectDB()
  const collection = db.collection(COLLECTION)
  await collection.insertOne({
    ...event,
    receivedAt: new Date()
  })
}

export async function getRecentWebhookEvents(limit: number = 25) {
  const db = await connectDB()
  const collection = db.collection(COLLECTION)
  return collection.find({}).sort({ receivedAt: -1 }).limit(limit).toArray()
}

export async function processWebhookEvent(event: any) {
  await storeWebhookEvent(event)

  try {
    if (event.topic === 'orders' && event.resource) {
      const orderId = parseInt(event.resource.split('/').pop() || '', 10)
      if (!isNaN(orderId)) {
        await syncOrderById(orderId)
      }
    }
  } catch (error) {
    console.error('Error processing Mercado Libre webhook event:', error)
  }
}

