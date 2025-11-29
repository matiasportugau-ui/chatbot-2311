export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server'
import { connectDB } from '@/lib/mongodb'
import { withRateLimit } from '@/lib/rate-limit'

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
          { success: false, error: 'Unauthorized - Authentication required for system settings' },
          { status: 401 }
        )
      }
      
      const { validateToken, checkAdminRole } = await import('@/lib/auth')
      const user = await validateToken(token)
      if (!user || !checkAdminRole(user)) {
        return NextResponse.json(
          { success: false, error: 'Forbidden - Admin access required for system settings' },
          { status: 403 }
        )
      }
    }
    
    const userId = searchParams.get('userId')

    const db = await connectDB()
    const settings = db.collection('settings')

    const query: any = { scope }
    if (scope === 'user' && userId) {
      query.userId = userId
    }

    const settingsDoc = await settings.findOne(query)

    // Return default settings if none found
    const defaultSettings = {
      theme: 'light',
      language: 'es',
      notifications: {
        email: true,
        push: false,
        sms: false
      },
      dashboard: {
        refreshInterval: 30,
        itemsPerPage: 20
      },
      analytics: {
        dateRange: '30days',
        showCharts: true
      }
    }

    return NextResponse.json({
      success: true,
      data: settingsDoc?.settings || defaultSettings
    })
  } catch (error: any) {
    console.error('Settings GET API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
        data: {}
      },
      { status: 500 }
    )
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
        return NextResponse.json(
          { success: false, error: 'Unauthorized - Authentication required for system settings' },
          { status: 401 }
        )
      }
      
      const { validateToken, checkAdminRole } = await import('@/lib/auth')
      const user = await validateToken(token)
      if (!user || !checkAdminRole(user)) {
        return NextResponse.json(
          { success: false, error: 'Forbidden - Admin access required for system settings' },
          { status: 403 }
        )
      }
    }

    if (!newSettings || typeof newSettings !== 'object') {
      return NextResponse.json(
        { success: false, error: 'Settings object is required' },
        { status: 400 }
      )
    }

    // Validate settings structure
    const validationResult = validateSettings(newSettings)
    if (!validationResult.valid) {
      return NextResponse.json(
        {
          success: false,
          error: 'Settings validation failed',
          validationErrors: validationResult.errors
        },
        { status: 400 }
      )
    }

    const db = await connectDB()
    const settings = db.collection('settings')

    const query: any = { scope }
    if (scope === 'user' && userId) {
      query.userId = userId
    }

    // Update or insert settings
    await settings.updateOne(
      query,
      {
        $set: {
          settings: newSettings,
          updatedAt: new Date()
        },
        $setOnInsert: {
          scope,
          userId: scope === 'user' ? userId : undefined,
          createdAt: new Date()
        }
      },
      { upsert: true }
    )

    return NextResponse.json({
      success: true,
      data: newSettings,
      message: 'Settings updated successfully'
    })
  } catch (error: any) {
    console.error('Settings POST API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error'
      },
      { status: 500 }
    )
  }
}

function validateSettings(settings: any): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  // Validate theme
  if (settings.theme && !['light', 'dark', 'auto'].includes(settings.theme)) {
    errors.push('Invalid theme. Must be: light, dark, or auto')
  }

  // Validate language
  if (settings.language && !['es', 'en', 'pt'].includes(settings.language)) {
    errors.push('Invalid language. Must be: es, en, or pt')
  }

  // Validate refresh interval
  if (settings.dashboard?.refreshInterval && 
      (typeof settings.dashboard.refreshInterval !== 'number' || 
       settings.dashboard.refreshInterval < 5 || 
       settings.dashboard.refreshInterval > 300)) {
    errors.push('Refresh interval must be between 5 and 300 seconds')
  }

  // Validate items per page
  if (settings.dashboard?.itemsPerPage && 
      (typeof settings.dashboard.itemsPerPage !== 'number' || 
       settings.dashboard.itemsPerPage < 10 || 
       settings.dashboard.itemsPerPage > 100)) {
    errors.push('Items per page must be between 10 and 100')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

// Export with rate limiting
export const GET = withRateLimit(getSettingsHandler, 60, 15 * 60 * 1000) // 60 requests per 15 minutes
export const POST = withRateLimit(postSettingsHandler, 30, 15 * 60 * 1000) // 30 requests per 15 minutes


