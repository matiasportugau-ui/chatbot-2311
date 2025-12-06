/**
 * Authentication Middleware for Next.js API Routes
 * Provides authentication and authorization utilities
 */

import { NextRequest, NextResponse } from 'next/server'

import { AuthenticatedUser, User } from '@/types/user'

export type AuthUser = User

/**
 * Validates an authentication token
 * @param token - Bearer token from Authorization header
 * @returns User object if valid, null otherwise
 */
export async function validateToken(token: string): Promise<AuthUser | null> {
  // Remove 'Bearer ' prefix if present
  const cleanToken = token.replace(/^Bearer\s+/i, '')

  // For now, use environment variable for simple API key authentication
  // In production, implement proper JWT validation or OAuth
  const apiKey = process.env.API_KEY || process.env.ADMIN_API_KEY

  if (!apiKey) {
    // If no API key configured, allow all requests (development mode)
    // In production, this should be required
    if (process.env.NODE_ENV === 'production') {
      return null
    }
    return { id: 'dev-user', role: 'admin' }
  }

  // Simple API key validation
  if (cleanToken === apiKey) {
    return { id: 'api-user', role: 'admin' }
  }

  // Check for user API keys (if configured)
  const userApiKey = process.env.USER_API_KEY
  if (userApiKey && cleanToken === userApiKey) {
    return { id: 'user', role: 'user' }
  }

  return null
}

/**
 * Checks if user has admin role
 * @param user - Authenticated user object
 * @returns true if user is admin
 */
export function checkAdminRole(user: AuthUser | null): boolean {
  return user?.role === 'admin'
}

/**
 * Middleware to require authentication
 * @param handler - Route handler function
 * @returns Wrapped handler with authentication check
 */
export function requireAuth(
  handler: (request: NextRequest, user: AuthUser) => Promise<NextResponse>
) {
  return async (request: NextRequest) => {
    const token = request.headers.get('Authorization')

    if (!token) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized - Missing token' },
        { status: 401 }
      )
    }

    // Validate token
    const user = await validateToken(token)
    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized - Invalid token' },
        { status: 401 }
      )
    }

    // Call handler with authenticated user
    return handler(request, user)
  }
}

/**
 * Middleware to require admin access
 * @param handler - Route handler function
 * @returns Wrapped handler with admin check
 */
export function requireAdmin(
  handler: (request: NextRequest, user: AuthUser) => Promise<NextResponse>
) {
  return async (request: NextRequest) => {
    const token = request.headers.get('Authorization')

    if (!token) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized - Missing token' },
        { status: 401 }
      )
    }

    // Validate token
    const user = await validateToken(token)
    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized - Invalid token' },
        { status: 401 }
      )
    }

    // Check admin role
    if (!checkAdminRole(user)) {
      return NextResponse.json(
        { success: false, error: 'Forbidden - Admin access required' },
        { status: 403 }
      )
    }

    // Call handler with authenticated admin user
    return handler(request, user)
  }
}

/**
 * Optional authentication - adds user to request if token is valid
 * @param handler - Route handler function
 * @returns Wrapped handler with optional auth
 */
export function optionalAuth(
  handler: (
    request: NextRequest,
    user: AuthenticatedUser
  ) => Promise<NextResponse>
) {
  return async (request: NextRequest) => {
    const token = request.headers.get('Authorization')
    let user: AuthenticatedUser = null

    if (token) {
      user = await validateToken(token)
    }

    return handler(request, user)
  }
}
