export const dynamic = 'force-dynamic'

<<<<<<< Updated upstream
import { getSharedContextService } from '@/lib/shared-context-service'
import { NextRequest, NextResponse } from 'next/server'
=======
import {
  errorResponse,
  notFoundResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { withRateLimit } from '@/lib/rate-limit'
import { getSharedContextService } from '@/lib/shared-context-service'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'
>>>>>>> Stashed changes

/**
 * Context Export API
 * GET /api/context/export?sessionId=xxx
 * Exports conversation context as JSON
 */

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('sessionId')
    const userPhone = searchParams.get('userPhone')

    if (!sessionId || !userPhone) {
      return validationErrorResponse(
        ['sessionId and userPhone are required'],
        'Missing required parameters'
      )
    }

    const service = getSharedContextService()
    const context = await service.getContext(sessionId, userPhone)

    if (!context) {
      return notFoundResponse('Context')
    }

    // Get session metadata
    const session = await service.getSession(sessionId)

    // Prepare export data
    const exportData = {
      session_id: sessionId,
      user_phone: userPhone,
      exported_at: new Date().toISOString(),
      session_metadata: session,
      context: context,
    }

<<<<<<< Updated upstream
    return NextResponse.json({
      success: true,
      data: exportData,
    })
  } catch (error: any) {
    console.error('Context Export API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
=======
    return successResponse(exportData)
  } catch (error: unknown) {
    console.error('Context Export API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}
