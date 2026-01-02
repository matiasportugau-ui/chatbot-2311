export const dynamic = 'force-dynamic'

import { connectDB } from '@/lib/mongodb'
import { withRateLimit } from '@/lib/rate-limit'
import { SettingsDocument } from '@/types/settings'
import { NextRequest, NextResponse } from 'next/server'
import {
  successResponse,
  errorResponse,
  unauthorizedResponse,
  forbiddenResponse,
  validationErrorResponse,
} from '@/lib/api-response'

/**
 * Settings API Endpoint
 * GET /api/settings - Retrieve settings
 * POST /api/settings - Update settings
 *
 * Settings are stored per user or system-wide
 * Requires authentication for system-wide settings
 */
async function getSettingsHandler(request: NextRequest) {
  try {
    // Check authentication for system settings
    const { searchParams } = new URL(request.url)
    const scope = searchParams.get('scope') || 'user'

    if (scope === 'system') {
      const token = request.headers.get('Authorization')
      if (!token) {
        return NextResponse.json(
          {
            success: false,
            error: 'Unauthorized - Authentication required for system settings',
          },
          { status: 401 }
        )
      }

      const { validateToken, checkAdminRole } = await import('@/lib/auth')
      const user = await validateToken(token)
      if (!user || !checkAdminRole(user)) {
        return NextResponse.json(
          {
            success: false,
            error: 'Forbidden - Admin access required for system settings',
          },
          { status: 403 }
        )
      }
    }

    const userId = searchParams.get('userId')

    const db = await connectDB()
    const settings = db.collection('settings')

    const query: Record<string, unknown> = { scope }
    if (scope === 'user' && userId) {
      query.userId = userId
    }

    const settingsDoc = (await settings.findOne(
      query
    )) as SettingsDocument | null

    // Return default settings if none found
    const defaultSettings = {
      theme: 'light',
      language: 'es',
      notifications: {
        email: true,
        push: false,
        sms: false,
      },
      dashboard: {
        refreshInterval: 30,
        itemsPerPage: 20,
      },
      analytics: {
        dateRange: '30days',
        showCharts: true,
      },
    }

    // SettingsDocument has 'value' property, not 'settings'
    const settingsValue = settingsDoc?.value as
      | Record<string, unknown>
      | undefined
    return successResponse(settingsValue || defaultSettings)
  } catch (error: unknown) {
    console.error('Settings GET API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}

async function postSettingsHandler(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, scope = 'user', settings: newSettings } = body

    // Check authentication for system settings
    if (scope === 'system') {
      const token = request.headers.get('Authorization')
      if (!token) {
        return unauthorizedResponse('Authentication required for system settings')
      }

      const { validateToken, checkAdminRole } = await import('@/lib/auth')
      const user = await validateToken(token)
      if (!user || !checkAdminRole(user)) {
        return forbiddenResponse('Admin access required for system settings')
      }
    }

    if (!newSettings || typeof newSettings !== 'object') {
      return validationErrorResponse(
        ['Settings object is required'],
        'Missing required field'
      )
    }

    // Validate settings structure
    const validationResult = validateSettings(newSettings)
    if (!validationResult.valid) {
      return validationErrorResponse(
        validationResult.errors,
        'Settings validation failed'
      )
    }

    const db = await connectDB()
    const settings = db.collection('settings')

    const query: Record<string, unknown> = { scope }
    if (scope === 'user' && userId) {
      query.userId = userId
    }

    // Update or insert settings
    await settings.updateOne(
      query,
      {
        $set: {
          settings: newSettings,
          updatedAt: new Date(),
        },
        $setOnInsert: {
          scope,
          userId: scope === 'user' ? userId : undefined,
          createdAt: new Date(),
        },
      },
      { upsert: true }
    )

    return successResponse(newSettings, 'Settings updated successfully')
  } catch (error: unknown) {
    console.error('Settings POST API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}

function validateSettings(settings: Record<string, unknown>): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []

  // Validate theme
  const theme = settings.theme
  if (
    theme &&
    typeof theme === 'string' &&
    !['light', 'dark', 'auto'].includes(theme)
  ) {
    errors.push('Invalid theme. Must be: light, dark, or auto')
  }

  // Validate language
  const language = settings.language
  if (
    language &&
    typeof language === 'string' &&
    !['es', 'en', 'pt'].includes(language)
  ) {
    errors.push('Invalid language. Must be: es, en, or pt')
  }

  // Validate refresh interval
  const dashboard = settings.dashboard
  if (
    dashboard &&
    typeof dashboard === 'object' &&
    'refreshInterval' in dashboard &&
    typeof dashboard.refreshInterval === 'number'
  ) {
    const refreshInterval = dashboard.refreshInterval
    if (refreshInterval < 5 || refreshInterval > 300) {
      errors.push('Refresh interval must be between 5 and 300 seconds')
    }
  }

  // Validate items per page
  if (
    dashboard &&
    typeof dashboard === 'object' &&
    'itemsPerPage' in dashboard &&
    typeof dashboard.itemsPerPage === 'number'
  ) {
    const itemsPerPage = dashboard.itemsPerPage
    if (itemsPerPage < 10 || itemsPerPage > 100) {
      errors.push('Items per page must be between 10 and 100')
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

// Export with rate limiting
export const GET = withRateLimit(getSettingsHandler, 60, 15 * 60 * 1000) // 60 requests per 15 minutes
export const POST = withRateLimit(postSettingsHandler, 30, 15 * 60 * 1000) // 30 requests per 15 minutes
