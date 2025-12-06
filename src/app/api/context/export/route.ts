export const dynamic = 'force-dynamic'

import {
  errorResponse,
  notFoundResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { getSharedContextService } from '@/lib/shared-context-service'
import { NextRequest } from 'next/server'

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

    return successResponse(exportData)
  } catch (error: unknown) {
    console.error('Context Export API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}
