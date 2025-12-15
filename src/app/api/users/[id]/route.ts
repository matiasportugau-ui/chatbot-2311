import { NextRequest, NextResponse } from 'next/server'
import { requirePermission, getCurrentUserId } from '@/lib/auth/session'
import {
  getSafeUserById,
  updateUser,
  deleteUser
} from '@/lib/auth/auth-service'
import type { UpdateUserInput } from '@/types/user'

interface RouteContext {
  params: Promise<{ id: string }>
}

/**
 * GET /api/users/[id]
 * Get user details
 */
export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  try {
    await requirePermission('users:read')

    const { id } = await context.params

    const user = await getSafeUserById(id)

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    return NextResponse.json({ user })
  } catch (error) {
    console.error('Get user error:', error)

    if (error instanceof Error) {
      if (error.message.includes('Unauthorized')) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      }
      if (error.message.includes('Forbidden')) {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
      }
    }

    return NextResponse.json(
      { error: 'Failed to get user' },
      { status: 500 }
    )
  }
}

/**
 * PATCH /api/users/[id]
 * Update user
 */
export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const currentUserId = await getCurrentUserId()
    const { id } = await context.params

    // Check permissions - users can update themselves, or need update permission
    const isSelf = currentUserId === id
    if (!isSelf) {
      await requirePermission('users:update')
    }

    const body = await request.json()
    const updateData: UpdateUserInput = {}

    // Validate and build update object
    if (body.name !== undefined) updateData.name = body.name
    if (body.role !== undefined) {
      // Only admins can change roles
      if (!isSelf) {
        await requirePermission('users:update')
      } else {
        return NextResponse.json(
          { error: 'You cannot change your own role' },
          { status: 403 }
        )
      }

      const validRoles = ['admin', 'manager', 'sales', 'viewer']
      if (!validRoles.includes(body.role)) {
        return NextResponse.json(
          { error: `Invalid role. Must be one of: ${validRoles.join(', ')}` },
          { status: 400 }
        )
      }
      updateData.role = body.role
    }

    if (body.avatar !== undefined) updateData.avatar = body.avatar
    if (body.settings !== undefined) updateData.settings = body.settings

    const updatedUser = await updateUser(id, updateData)

    // Return user without password
    const { password: _, ...safeUser } = updatedUser

    return NextResponse.json({
      message: 'User updated successfully',
      user: {
        ...safeUser,
        id: safeUser._id?.toString()
      }
    })
  } catch (error) {
    console.error('Update user error:', error)

    if (error instanceof Error) {
      if (error.message.includes('Unauthorized')) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      }
      if (error.message.includes('Forbidden')) {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
      }
      if (error.message.includes('not found')) {
        return NextResponse.json({ error: 'User not found' }, { status: 404 })
      }
    }

    return NextResponse.json(
      { error: 'Failed to update user' },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/users/[id]
 * Delete user (admin only)
 */
export async function DELETE(
  request: NextRequest,
  context: RouteContext
) {
  try {
    await requirePermission('users:delete')

    const currentUserId = await getCurrentUserId()
    const { id } = await context.params

    // Prevent self-deletion
    if (currentUserId === id) {
      return NextResponse.json(
        { error: 'You cannot delete your own account' },
        { status: 403 }
      )
    }

    await deleteUser(id)

    return NextResponse.json({
      message: 'User deleted successfully'
    })
  } catch (error) {
    console.error('Delete user error:', error)

    if (error instanceof Error) {
      if (error.message.includes('Unauthorized')) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      }
      if (error.message.includes('Forbidden')) {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
      }
      if (error.message.includes('not found')) {
        return NextResponse.json({ error: 'User not found' }, { status: 404 })
      }
    }

    return NextResponse.json(
      { error: 'Failed to delete user' },
      { status: 500 }
    )
  }
}
