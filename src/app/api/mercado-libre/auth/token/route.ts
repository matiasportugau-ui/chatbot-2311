<<<<<<< Updated upstream
import { NextResponse } from 'next/server'
import { getGrantStatus, refreshTokens } from '@/lib/mercado-libre/client'
=======
import { errorResponse, successResponse } from '@/lib/api-response'
import { getGrantStatus, refreshTokens } from '@/lib/mercado-libre/client'
import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'
>>>>>>> Stashed changes

export async function GET() {
  try {
    const status = await getGrantStatus()
    return successResponse(status)
  } catch (error: unknown) {
    console.error('Error fetching Mercado Libre grant status:', error)
<<<<<<< Updated upstream
    return NextResponse.json({ error: 'Unable to fetch Mercado Libre status' }, { status: 500 })
=======
    return errorResponse('Unable to fetch Mercado Libre status', 500)
>>>>>>> Stashed changes
  }
}

export async function POST() {
  try {
    const tokens = await refreshTokens()
<<<<<<< Updated upstream
    return NextResponse.json({
      success: true,
      expiresIn: tokens.expires_in
=======
    return successResponse({
      expiresIn: tokens.expires_in,
>>>>>>> Stashed changes
    })
  } catch (error: unknown) {
    console.error('Error refreshing Mercado Libre token:', error)
<<<<<<< Updated upstream
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Unable to refresh Mercado Libre token'
      },
      { status: 500 }
    )
=======
    const errorMessage =
      error instanceof Error
        ? error.message
        : 'Unable to refresh Mercado Libre token'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}

