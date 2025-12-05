
import { errorResponse, successResponse } from '@/lib/api-response'
import { startAuthorization } from '@/lib/mercado-libre/client'
import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'


export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    const { returnTo } = body || {}

    const result = await startAuthorization(
      typeof returnTo === 'string' ? returnTo : undefined
    )
    return successResponse(result)
  } catch (error: unknown) {
    console.error('Error initiating Mercado Libre OAuth:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)

  }
}

