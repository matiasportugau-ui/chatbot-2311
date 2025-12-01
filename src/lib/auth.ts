/**
 * Authentication Middleware
 * Provides authentication and authorization helpers for API routes
 */

import { NextRequest, NextResponse } from 'next/server'

type RequestHandler = (
  request: NextRequest,
  context?: any
) => Promise<NextResponse>

interface UserInfo {
  id?: string
  role?: string
  phone?: string
  isAdmin?: boolean
  [key: string]: any
}

// Constants
const JWT_PARTS_COUNT = 3
const MIN_API_TOKEN_LENGTH = 32

/**
 * Validate token format
 */
function isValidTokenFormat(token: string): boolean {
  if (!token) return false
  
  const parts = token.split('.')
  if (parts.length === JWT_PARTS_COUNT) {
    // Basic JWT structure check
    return true
  }
  
  // Allow simple API tokens
  return token.length >= MIN_API_TOKEN_LENGTH
}

/**
 * Decode a JWT token (placeholder - implement with your JWT library)
 */
function decodeToken(token: string): UserInfo | null {
  if (!token) return null
  
  try {
    const parts = token.split('.')
    if (parts.length === 3) {
      // Basic JWT decoding (payload is in the second part)
      const payload = JSON.parse(
        Buffer.from(parts[1], 'base64').toString('utf-8')
      )
      return payload
    }
  } catch {
    // Invalid token format
  }
  
  return null
}

/**
 * Check if request has valid authentication
 */
function isAuthenticated(request: NextRequest): boolean {
  // Check for API key in header
  const apiKey = request.headers.get('x-api-key')
  if (apiKey && apiKey === process.env.API_SECRET_KEY) {
    return true
  }

  // Check for Authorization header (Bearer token)
  const authHeader = request.headers.get('authorization')
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.slice(7)
    if (token && (process.env.NODE_ENV === 'development' || isValidTokenFormat(token))) {
      return true
    }
  }

  // Check for session cookie (for dashboard access)
  const sessionCookie = request.cookies.get('session')
  if (sessionCookie?.value) {
    return true
  }

  // In development mode, allow requests without authentication
  if (process.env.NODE_ENV === 'development') {
    return true
  }

  return false
}

/**
 * Check if request has admin privileges
 */
function isAdmin(request: NextRequest): boolean {
  // Check for admin API key
  const apiKey = request.headers.get('x-api-key')
  if (apiKey && apiKey === process.env.ADMIN_API_KEY) {
    return true
  }

  // Check for admin role in Authorization header
  const authHeader = request.headers.get('authorization')
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.slice(7)
    const decoded = decodeToken(token)
    if (decoded?.role === 'admin') {
      return true
    }
  }

  // Check for admin cookie
  const adminCookie = request.cookies.get('admin_session')
  if (adminCookie?.value) {
    return true
  }

  // In development mode, allow admin access
  if (process.env.NODE_ENV === 'development') {
    return true
  }

  return false
}

/**
 * Higher-order function to require authentication
 */
export function requireAuth(handler: RequestHandler): RequestHandler {
  return async (request: NextRequest, context?: any): Promise<NextResponse> => {
    if (!isAuthenticated(request)) {
      return NextResponse.json(
        {
          success: false,
          error: 'Authentication required',
          message: 'Please provide a valid API key or authentication token',
        },
        { status: 401 }
      )
    }

    return handler(request, context)
  }
}

/**
 * Higher-order function to require admin privileges
 */
export function requireAdmin(handler: RequestHandler): RequestHandler {
  return async (request: NextRequest, context?: any): Promise<NextResponse> => {
    if (!isAuthenticated(request)) {
      return NextResponse.json(
        {
          success: false,
          error: 'Authentication required',
          message: 'Please provide a valid API key or authentication token',
        },
        { status: 401 }
      )
    }

    if (!isAdmin(request)) {
      return NextResponse.json(
        {
          success: false,
          error: 'Admin privileges required',
          message: 'This endpoint requires administrator access',
        },
        { status: 403 }
      )
    }

    return handler(request, context)
  }
}

/**
 * Extract user information from request
 */
export function getUserFromRequest(request: NextRequest): UserInfo | null {
  const authHeader = request.headers.get('authorization')
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.slice(7)
    return decodeToken(token)
  }
  
  return null
}

/**
 * Validate a token and return user info (exported for dynamic imports)
 */
export async function validateToken(authHeader: string): Promise<UserInfo | null> {
  if (!authHeader) return null
  
  // Extract token from "Bearer xxx" format
  const token = authHeader.startsWith('Bearer ')
    ? authHeader.slice(7)
    : authHeader

  if (!isValidTokenFormat(token)) {
    return null
  }

  return decodeToken(token)
}

/**
 * Check if user has admin role (exported for dynamic imports)
 */
export function checkAdminRole(user: UserInfo | null): boolean {
  if (!user) return false
  
  // Check role
  if (user.role === 'admin') return true
  
  // Check admin flag
  if (user.isAdmin === true) return true
  
  // In development, allow all authenticated users
  if (process.env.NODE_ENV === 'development') return true
  
  return false
}
