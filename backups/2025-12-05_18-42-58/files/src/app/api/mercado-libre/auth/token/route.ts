
import { errorResponse, successResponse } from '@/lib/api-response'
import { getGrantStatus, refreshTokens } from '@/lib/mercado-libre/client'
import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'


export async function GET() {
  try {
    const status = await getGrantStatus()
    return successResponse(status)
  } catch (error: unknown) {
    console.error('Error fetching Mercado Libre grant status:', error)

    return errorResponse('Unable to fetch Mercado Libre status', 500)

  }
}

export async function POST() {
  try {
    const tokens = await refreshTokens()

    return successResponse({
      expiresIn: tokens.expires_in,

    })
  } catch (error: unknown) {
    console.error('Error refreshing Mercado Libre token:', error)

    const errorMessage =
      error instanceof Error
        ? error.message
        : 'Unable to refresh Mercado Libre token'
    return errorResponse(errorMessage, 500)

  }
}

