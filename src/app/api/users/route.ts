import { NextRequest, NextResponse } from 'next/server'
import { requirePermission } from '@/lib/auth/session'
import { createUser, listUsers } from '@/lib/auth/auth-service'
import type { CreateUserInput } from '@/types/user'

/**
 * GET /api/users
 * List all users (admin/manager only)
 */
export async function GET(request: NextRequest) {
  try {
    await requirePermission('users:list')

    const searchParams = request.nextUrl.searchParams
    const limit = parseInt(searchParams.get('limit') || '50')
    const skip = parseInt(searchParams.get('skip') || '0')
    const role = searchParams.get('role') || undefined

    const result = await listUsers({
      limit,
      skip,
      role
    })

    return NextResponse.json(result)
  } catch (error) {
    console.error('List users error:', error)

    if (error instanceof Error) {
      if (error.message.includes('Unauthorized')) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      }
      if (error.message.includes('Forbidden')) {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
      }
    }

    return NextResponse.json(
      { error: 'Failed to list users' },
      { status: 500 }
    )
  }
}

/**
 * POST /api/users
 * Create a new user (admin only)
 */
export async function POST(request: NextRequest) {
  try {
    await requirePermission('users:create')

    const body = await request.json()

    // Validate required fields
    const { email, password, name, role } = body as CreateUserInput

    if (!email || !password || !name || !role) {
      return NextResponse.json(
        { error: 'Missing required fields: email, password, name, role' },
        { status: 400 }
      )
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      )
    }

    // Validate role
    const validRoles = ['admin', 'manager', 'sales', 'viewer']
    if (!validRoles.includes(role)) {
      return NextResponse.json(
        { error: `Invalid role. Must be one of: ${validRoles.join(', ')}` },
        { status: 400 }
      )
    }

    const user = await createUser({ email, password, name, role })

    // Return user without password
    const { password: _, ...safeUser } = user

    return NextResponse.json(
      {
        message: 'User created successfully',
        user: {
          ...safeUser,
          id: safeUser._id?.toString()
        }
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Create user error:', error)

    if (error instanceof Error) {
      if (error.message.includes('Unauthorized')) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      }
      if (error.message.includes('Forbidden')) {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
      }
      if (error.message.includes('already exists')) {
        return NextResponse.json(
          { error: 'User with this email already exists' },
          { status: 409 }
        )
      }
      if (error.message.includes('Password must be')) {
        return NextResponse.json({ error: error.message }, { status: 400 })
      }
    }

    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 500 }
    )
  }
}
