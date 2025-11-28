export const dynamic = 'force-dynamic'

import { connectDB } from '@/lib/mongodb'
import { ObjectId } from 'mongodb'
import { NextRequest, NextResponse } from 'next/server'

/**
 * Notifications API Endpoint
 * GET /api/notifications - Retrieve notifications (with pagination)
 * POST /api/notifications - Create notification
 * PUT /api/notifications - Mark as read
 * DELETE /api/notifications - Delete notification
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '20')
    const type = searchParams.get('type')
    const status = searchParams.get('status') // 'read' | 'unread' | 'all'
    const dateFrom = searchParams.get('dateFrom')
    const dateTo = searchParams.get('dateTo')

    const db = await connectDB()
    const notifications = db.collection('notifications')

    // Build query
    const query: any = {}
    if (type) {
      query.type = type
    }
    if (status && status !== 'all') {
      query.read = status === 'read'
    }
    if (dateFrom || dateTo) {
      query.timestamp = {}
      if (dateFrom) {
        query.timestamp.$gte = new Date(dateFrom)
      }
      if (dateTo) {
        query.timestamp.$lte = new Date(dateTo)
      }
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

    return NextResponse.json({
      success: true,
      data: {
        notifications: results,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit),
        },
      },
    })
  } catch (error: any) {
    console.error('Notifications GET API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
        data: {
          notifications: [],
          pagination: { page: 1, limit: 20, total: 0, totalPages: 0 },
        },
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
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
      return NextResponse.json(
        { success: false, error: 'Type, title, and message are required' },
        { status: 400 }
      )
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

    return NextResponse.json({
      success: true,
      data: {
        ...notification,
        _id: result.insertedId.toString(),
      },
      message: 'Notification created successfully',
    })
  } catch (error: any) {
    console.error('Notifications POST API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { id, read } = body

    if (!id) {
      return NextResponse.json(
        { success: false, error: 'Notification ID is required' },
        { status: 400 }
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
      return NextResponse.json(
        { success: false, error: 'Invalid notification ID format' },
        { status: 400 }
      )
    }
    const objectId = new ObjectId(id)

    const result = await notifications.updateOne(
      { _id: objectId },
      { $set: update }
    )

    if (result.matchedCount === 0) {
      return NextResponse.json(
        { success: false, error: 'Notification not found' },
        { status: 404 }
      )
    }

    return NextResponse.json({
      success: true,
      message: 'Notification updated successfully',
    })
  } catch (error: any) {
    console.error('Notifications PUT API Error:', error)
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
    const id = searchParams.get('id')

    if (!id) {
      return NextResponse.json(
        { success: false, error: 'Notification ID is required' },
        { status: 400 }
      )
    }

    const db = await connectDB()
    const notifications = db.collection('notifications')

    // Convert string id to ObjectId
    if (!ObjectId.isValid(id)) {
      return NextResponse.json(
        { success: false, error: 'Invalid notification ID format' },
        { status: 400 }
      )
    }
    const objectId = new ObjectId(id)

    const result = await notifications.deleteOne({ _id: objectId })

    if (result.deletedCount === 0) {
      return NextResponse.json(
        { success: false, error: 'Notification not found' },
        { status: 404 }
      )
    }

    return NextResponse.json({
      success: true,
      message: 'Notification deleted successfully',
    })
  } catch (error: any) {
    console.error('Notifications DELETE API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}
