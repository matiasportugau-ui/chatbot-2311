import { NextRequest, NextResponse } from 'next/server'
import {
  getRecentWebhookEvents,
  processWebhookEvent,
  verifyWebhookSignature
} from '@/lib/mercado-libre/webhook-service'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const url = new URL(request.url)

  if (url.searchParams.get('events') === 'true') {
    const events = await getRecentWebhookEvents()
    return NextResponse.json({ events })
  }

  return NextResponse.json({ status: 'ready' })
}

export async function POST(request: NextRequest) {
  const signature = request.headers.get('x-hub-signature')
  const rawBody = await request.text()

  if (!verifyWebhookSignature(rawBody, signature)) {
    return NextResponse.json({ error: 'Firma inválida' }, { status: 401 })
  }

  try {
    const event = JSON.parse(rawBody)
    await processWebhookEvent(event)
    return NextResponse.json({ received: true })
  } catch (error) {
    console.error('Error handling Mercado Libre webhook:', error)
    return NextResponse.json({ error: 'Error procesando webhook' }, { status: 500 })
  }
}

