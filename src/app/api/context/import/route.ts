export const dynamic = 'force-dynamic'

<<<<<<< Updated upstream
import { getSharedContextService } from '@/lib/shared-context-service'
import { NextRequest, NextResponse } from 'next/server'
=======
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { withRateLimit } from '@/lib/rate-limit'
import { getSharedContextService } from '@/lib/shared-context-service'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'
>>>>>>> Stashed changes

/**
 * Context Import API
 * POST /api/context/import
 * Imports conversation context from JSON
 *
 * Request body:
 * - sessionId: string (required)
 * - userPhone: string (required)
 * - context: object (required) - Context data to import
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { sessionId, userPhone, context } = body

    if (!sessionId || !userPhone || !context) {
      return validationErrorResponse(
        ['sessionId, userPhone, and context are required'],
        'Missing required fields'
      )
    }

    const service = getSharedContextService()
    const success = await service.saveContext(sessionId, {
      ...context,
      user_phone: userPhone,
      session_id: sessionId,
      last_updated: new Date(),
    })

    if (!success) {
      return errorResponse('Failed to import context', 500)
    }

    return successResponse(
      {
        sessionId,
        userPhone,
      },
<<<<<<< Updated upstream
    })
  } catch (error: any) {
    console.error('Context Import API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
=======
      'Context imported successfully'
    )
  } catch (error: unknown) {
    console.error('Context Import API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}
