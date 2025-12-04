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
 * Shared Context API Route
 * Unified endpoint for all agents to access conversation context
 */

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action') || 'get'
    const sessionId = searchParams.get('sessionId')
    const userPhone = searchParams.get('userPhone')

    const service = getSharedContextService()

    switch (action) {
      case 'get': {
        if (!sessionId || !userPhone) {
          return validationErrorResponse(
            ['sessionId and userPhone are required'],
            'Missing required parameters'
          )
        }
        const context = await service.getContext(sessionId, userPhone)
        if (!context) {
          return notFoundResponse('Context')
        }
        return successResponse(context)
      }

      case 'session': {
        if (!sessionId) {
          return validationErrorResponse(
            ['sessionId is required'],
            'Missing required parameter'
          )
        }
        const session = await service.getSession(sessionId)
        if (!session) {
          return notFoundResponse('Session')
        }
        return successResponse(session)
      }

      case 'list_sessions': {
        let limit = Number.parseInt(searchParams.get('limit') || '50', 10)
        // Validate limit to prevent NaN
        if (Number.isNaN(limit) || limit <= 0) {
          limit = 50 // Use default if invalid
        }
        const sessions = await service.listSessions(
          userPhone || undefined,
          limit
        )
        return successResponse(sessions)
      }

      default:
        return errorResponse(`Invalid action: ${action}`, 400)
    }
  } catch (error: unknown) {
    console.error('Shared Context GET API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action } = body

    const service = getSharedContextService()

    switch (action) {
      case 'save': {
        const { sessionId, context } = body
        if (!sessionId || !context) {
          return validationErrorResponse(
            ['sessionId and context are required'],
            'Missing required parameters'
          )
        }
        const saved = await service.saveContext(sessionId, context)
        if (saved) {
          return successResponse({ saved: true }, 'Context saved')
        }
        return errorResponse('Failed to save context', 500)
      }

      case 'add_message': {
        const { sessionId, message, role, metadata } = body
        if (!sessionId || !message || !role) {
          return validationErrorResponse(
            ['sessionId, message, and role are required'],
            'Missing required parameters'
          )
        }
        const added = await service.addMessage(
          sessionId,
          message,
          role,
          metadata
        )
        if (added) {
          return successResponse({ added: true }, 'Message added')
        }
        return errorResponse('Failed to add message', 500)
      }

      case 'create_session': {
        const { userPhone, initialMessage, metadata } = body
        if (!userPhone) {
          return validationErrorResponse(
            ['userPhone is required'],
            'Missing required parameter'
          )
        }
        const sessionId = await service.createSession(
          userPhone,
          initialMessage,
          metadata
        )
        return successResponse({ session_id: sessionId }, 'Session created')
      }

      default:
        return errorResponse(`Invalid action: ${action}`, 400)
    }
  } catch (error: unknown) {
    console.error('Shared Context POST API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action') || 'invalidate_cache'

    if (action === 'invalidate_cache') {
      // Cache invalidation would be handled by the service
      // For now, just return success
      return successResponse({ invalidated: true }, 'Cache invalidated')
    }

    return errorResponse(`Invalid action: ${action}`, 400)
  } catch (error: unknown) {
    console.error('Shared Context DELETE API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}
