import { NextRequest, NextResponse } from 'next/server'
import {
  errorResponse,
  successResponse,
  unauthorizedResponse,
} from '@/lib/api-response'
import {
  getRecentWebhookEvents,
  processWebhookEvent,
  verifyWebhookSignature
} from '@/lib/mercado-libre/webhook-service'
<<<<<<< Updated upstream
=======
import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'
>>>>>>> Stashed changes

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const url = new URL(request.url)

  if (url.searchParams.get('events') === 'true') {
    const events = await getRecentWebhookEvents()
    return successResponse({ events })
  }

  return successResponse({ status: 'ready' })
}

export async function POST(request: NextRequest) {
  const signature = request.headers.get('x-hub-signature')
  const rawBody = await request.text()

  if (!verifyWebhookSignature(rawBody, signature)) {
    return unauthorizedResponse('Firma inválida')
  }

  try {
    const event = JSON.parse(rawBody)
    await processWebhookEvent(event)
    return successResponse({ received: true })
  } catch (error: unknown) {
    console.error('Error handling Mercado Libre webhook:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ error: 'Error procesando webhook' }, { status: 500 })
=======
    return errorResponse('Error procesando webhook', 500)
>>>>>>> Stashed changes
  }
}

