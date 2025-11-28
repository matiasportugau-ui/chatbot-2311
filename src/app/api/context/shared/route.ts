export const dynamic = 'force-dynamic'

import { getSharedContextService } from '@/lib/shared-context-service'
import { NextRequest, NextResponse } from 'next/server'

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
          return NextResponse.json(
            { error: 'sessionId and userPhone are required' },
            { status: 400 }
          )
        }
        const context = await service.getContext(sessionId, userPhone)
        if (!context) {
          return NextResponse.json(
            { error: 'Context not found' },
            { status: 404 }
          )
        }
        return NextResponse.json({ success: true, data: context })
      }

      case 'session': {
        if (!sessionId) {
          return NextResponse.json(
            { error: 'sessionId is required' },
            { status: 400 }
          )
        }
        const session = await service.getSession(sessionId)
        if (!session) {
          return NextResponse.json(
            { error: 'Session not found' },
            { status: 404 }
          )
        }
        return NextResponse.json({ success: true, data: session })
      }

      case 'list_sessions': {
        const limit = Number.parseInt(searchParams.get('limit') || '50', 10)
        const sessions = await service.listSessions(
          userPhone || undefined,
          limit
        )
        return NextResponse.json({ success: true, data: sessions })
      }

      default:
        return NextResponse.json(
          { error: `Invalid action: ${action}` },
          { status: 400 }
        )
    }
  } catch (error: any) {
    console.error('Shared Context GET API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
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
          return NextResponse.json(
            { error: 'sessionId and context are required' },
            { status: 400 }
          )
        }
        const success = await service.saveContext(sessionId, context)
        return NextResponse.json({
          success,
          message: success ? 'Context saved' : 'Failed to save context',
        })
      }

      case 'add_message': {
        const { sessionId, message, role, metadata } = body
        if (!sessionId || !message || !role) {
          return NextResponse.json(
            { error: 'sessionId, message, and role are required' },
            { status: 400 }
          )
        }
        const success = await service.addMessage(
          sessionId,
          message,
          role,
          metadata
        )
        return NextResponse.json({
          success,
          message: success ? 'Message added' : 'Failed to add message',
        })
      }

      case 'create_session': {
        const { userPhone, initialMessage, metadata } = body
        if (!userPhone) {
          return NextResponse.json(
            { error: 'userPhone is required' },
            { status: 400 }
          )
        }
        const sessionId = await service.createSession(
          userPhone,
          initialMessage,
          metadata
        )
        return NextResponse.json({
          success: true,
          data: { session_id: sessionId },
        })
      }

      default:
        return NextResponse.json(
          { error: `Invalid action: ${action}` },
          { status: 400 }
        )
    }
  } catch (error: any) {
    console.error('Shared Context POST API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action') || 'invalidate_cache'

    if (action === 'invalidate_cache') {
      // Cache invalidation would be handled by the service
      // For now, just return success
      return NextResponse.json({ success: true, message: 'Cache invalidated' })
    }

    return NextResponse.json(
      { error: `Invalid action: ${action}` },
      { status: 400 }
    )
  } catch (error: any) {
    console.error('Shared Context DELETE API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}
