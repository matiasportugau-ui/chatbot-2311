export const dynamic = 'force-dynamic'

import {
  errorResponse,
  forbiddenResponse,
  notFoundResponse,
  paginatedResponse,
  successResponse,
  unauthorizedResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { optionalAuth, requireAuth } from '@/lib/auth'
import { connectDB } from '@/lib/mongodb'

import { withRateLimit } from '@/lib/rate-limit'
import { AuthenticatedUser } from '@/types/user'
import { ObjectId } from 'mongodb'
import { NextRequest } from 'next/server'


/**
 * Notifications API Endpoint
 * GET /api/notifications - Retrieve notifications (with pagination)
 * POST /api/notifications - Create notification
 * PUT /api/notifications - Mark as read
 * DELETE /api/notifications - Delete notification

 *
 * Requires authentication for user-specific notifications
 */
async function getNotificationsHandler(
  request: NextRequest,
  user: AuthenticatedUser
) {

  try {
    const { searchParams } = new URL(request.url)
    let page = parseInt(searchParams.get('page') || '1', 10)
    let limit = parseInt(searchParams.get('limit') || '20', 10)

    // Validate page and limit to prevent NaN and division by zero
    if (Number.isNaN(page) || page <= 0) {
      page = 1 // Use default if invalid
    }
    if (Number.isNaN(limit) || limit <= 0) {
      limit = 20 // Use default if invalid
    }

    const type = searchParams.get('type')
    const status = searchParams.get('status') // 'read' | 'unread' | 'all'
    const dateFrom = searchParams.get('dateFrom')
    const dateTo = searchParams.get('dateTo')

    const db = await connectDB()
    const notifications = db.collection('notifications')


    // Build query with user isolation
    const query: Record<string, unknown> = {}

    // User isolation: users can only see their own notifications unless admin
    if (user && user.role !== 'admin') {
      query.userId = user.id || userId || 'unknown'
    } else if (userId && user?.role === 'admin') {
      // Admin can query specific user
      query.userId = userId
    } else if (user && user.role === 'admin') {
      // Admin can see all if no userId specified
    } else {
      // No auth - return empty
      return unauthorizedResponse('Authentication required')
    }


    if (type) {
      query.type = type
    }
    if (status && status !== 'all') {
      query.read = status === 'read'
    }
    if (dateFrom || dateTo) {
      const timestampFilter: { $gte?: Date; $lte?: Date } = {}
      if (dateFrom) {
        timestampFilter.$gte = new Date(dateFrom)
      }
      if (dateTo) {
        timestampFilter.$lte = new Date(dateTo)
      }
      query.timestamp = timestampFilter
    }

    // Get total count
    const total = await notifications.countDocuments(query)

    // Get paginated results
    const results = await notifications
      .find(query)
      .sort({ timestamp: -1 })
      .skip((page - 1) * limit)
      .limit(limit)
      .toArray()


    return paginatedResponse(results, page, total, limit)
  } catch (error: unknown) {

    console.error('Notifications GET API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}


async function postNotificationsHandler(
  request: NextRequest,
  user: AuthenticatedUser
) {

  try {
    const body = await request.json()
    const {
      type,
      title,
      message,
      userId,
      priority = 'normal',
      metadata = {},
    } = body

    if (!type || !title || !message) {
      return validationErrorResponse(
        ['Type, title, and message are required'],
        'Missing required fields'
      )
    }


    // User isolation: users can only create notifications for themselves unless admin
    const targetUserId = userId || (user ? user.id : null)
    if (!targetUserId) {
      return validationErrorResponse(
        ['User ID is required'],
        'Missing required field'
      )
    }

    if (user && user.role !== 'admin' && targetUserId !== user.id) {
      return forbiddenResponse('Cannot create notifications for other users')
    }


    const db = await connectDB()
    const notifications = db.collection('notifications')

    const notification = {
      type,
      title,
      message,
      userId: userId || 'system',
      priority: priority || 'normal',
      read: false,
      timestamp: new Date(),
      metadata,
      createdAt: new Date(),
    }

    const result = await notifications.insertOne(notification)

    return successResponse(
      {
        ...notification,
        _id: result.insertedId.toString(),
      },

      'Notification created successfully'
    )
  } catch (error: unknown) {

    console.error('Notifications POST API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}


async function putNotificationsHandler(
  request: NextRequest,
  user: AuthenticatedUser
) {

  try {
    const body = await request.json()
    const { id, read } = body

    if (!id) {
      return validationErrorResponse(
        ['Notification ID is required'],
        'Missing required field'
      )
    }

    const db = await connectDB()
    const notifications = db.collection('notifications')

    const update: any = { updatedAt: new Date() }
    if (read !== undefined) {
      update.read = read
      if (read) {
        update.readAt = new Date()
      }
    }

    // Convert string id to ObjectId
    if (!ObjectId.isValid(id)) {
      return validationErrorResponse(
        ['Invalid notification ID format'],
        'Invalid ID format'
      )
    }
    const objectId = new ObjectId(id)


    // User isolation: check if user owns this notification
    const notification = await notifications.findOne({ _id: objectId })
    if (!notification) {
      return notFoundResponse('Notification')
    }

    // Users can only update their own notifications unless admin
    if (user && user.role !== 'admin' && notification.userId !== user.id) {
      return forbiddenResponse("Cannot update other users' notifications")
    }


    const result = await notifications.updateOne(
      { _id: objectId },
      { $set: update }
    )

    if (result.matchedCount === 0) {

      return notFoundResponse('Notification')
    }

    return successResponse(
      { updated: true },
      'Notification updated successfully'
    )
  } catch (error: unknown) {

    console.error('Notifications PUT API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}


async function deleteNotificationsHandler(
  request: NextRequest,
  user: AuthenticatedUser
) {

  try {
    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')

    if (!id) {
      return validationErrorResponse(
        ['Notification ID is required'],
        'Missing required field'
      )
    }

    const db = await connectDB()
    const notifications = db.collection('notifications')

    // Convert string id to ObjectId
    if (!ObjectId.isValid(id)) {
      return validationErrorResponse(
        ['Invalid notification ID format'],
        'Invalid ID format'
      )
    }
    const objectId = new ObjectId(id)


    // User isolation: check if user owns this notification
    const notification = await notifications.findOne({ _id: objectId })
    if (!notification) {
      return notFoundResponse('Notification')
    }

    // Users can only delete their own notifications unless admin
    if (user && user.role !== 'admin' && notification.userId !== user.id) {
      return forbiddenResponse("Cannot delete other users' notifications")
    }

    const result = await notifications.deleteOne({ _id: objectId })

    if (result.deletedCount === 0) {
      return notFoundResponse('Notification')
    }

    return successResponse(
      { deleted: true },
      'Notification deleted successfully'
    )
  } catch (error: unknown) {

    console.error('Notifications DELETE API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}


// Export with authentication and rate limiting
export const GET = withRateLimit(
  optionalAuth(async (request: NextRequest, user: AuthenticatedUser | null) =>
    getNotificationsHandler(request, user)
  ),
  60, // 60 requests per 15 minutes
  15 * 60 * 1000
)
export const POST = withRateLimit(
  requireAuth(async (request: NextRequest, user: AuthenticatedUser) =>
    postNotificationsHandler(request, user)
  ),
  30, // 30 requests per 15 minutes
  15 * 60 * 1000
)
export const PUT = withRateLimit(
  requireAuth(async (request: NextRequest, user: AuthenticatedUser) =>
    putNotificationsHandler(request, user)
  ),
  30, // 30 requests per 15 minutes
  15 * 60 * 1000
)
export const DELETE = withRateLimit(
  requireAuth(async (request: NextRequest, user: AuthenticatedUser) =>
    deleteNotificationsHandler(request, user)
  ),
  30, // 30 requests per 15 minutes
  15 * 60 * 1000
)

