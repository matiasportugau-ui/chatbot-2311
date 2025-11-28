export const dynamic = 'force-dynamic'

import { getSharedContextService } from '@/lib/shared-context-service'
import { NextRequest, NextResponse } from 'next/server'

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
      return NextResponse.json(
        {
          success: false,
          error: 'sessionId, userPhone, and context are required',
        },
        { status: 400 }
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
      return NextResponse.json(
        {
          success: false,
          error: 'Failed to import context',
        },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      message: 'Context imported successfully',
      data: {
        sessionId,
        userPhone,
      },
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
  }
}
