import { NextResponse } from 'next/server'
import { createUser, getUserByEmail } from '@/lib/auth/auth-service'

/**
 * POST /api/seed-users
 * Create demo users for the CRM system
 */
export async function POST() {
  try {
    const users = [
      {
        email: 'admin@example.com',
        password: 'admin123',
        name: 'Admin User',
        role: 'admin' as const
      },
      {
        email: 'manager@example.com',
        password: 'manager123',
        name: 'Manager User',
        role: 'manager' as const
      },
      {
        email: 'sales@example.com',
        password: 'sales123',
        name: 'Sales User',
        role: 'sales' as const
      },
      {
        email: 'viewer@example.com',
        password: 'viewer123',
        name: 'Viewer User',
        role: 'viewer' as const
      }
    ]

    const results = []

    for (const userData of users) {
      const existing = await getUserByEmail(userData.email)

      if (existing) {
        results.push({
          email: userData.email,
          status: 'already_exists',
          role: userData.role
        })
      } else {
        await createUser(userData)
        results.push({
          email: userData.email,
          status: 'created',
          role: userData.role,
          password: userData.password
        })
      }
    }

    return NextResponse.json({
      success: true,
      message: 'User seeding complete',
      results,
      credentials: {
        admin: 'admin@example.com / admin123',
        manager: 'manager@example.com / manager123',
        sales: 'sales@example.com / sales123',
        viewer: 'viewer@example.com / viewer123'
      }
    })
  } catch (error) {
    console.error('Seed users error:', error)

    return NextResponse.json(
      {
        success: false,
        error: 'Failed to seed users',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
