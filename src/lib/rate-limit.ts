/**
 * Rate Limiting Middleware for Next.js API Routes
 * Provides in-memory rate limiting functionality
 */

import { NextRequest, NextResponse } from 'next/server'

interface RateLimitRecord {
  count: number
  resetTime: number
}

// In-memory rate limit store
// In production, consider using Redis for distributed rate limiting
const rateLimitMap = new Map<string, RateLimitRecord>()

// Cleanup old entries periodically (every 5 minutes)
if (typeof setInterval !== 'undefined') {
  setInterval(() => {
    const now = Date.now()
    // Use Array.from to avoid iteration issues with older TypeScript targets
    for (const [key, record] of Array.from(rateLimitMap.entries())) {
      if (now > record.resetTime) {
        rateLimitMap.delete(key)
      }
    }
  }, 5 * 60 * 1000) // 5 minutes
}

/**
 * Gets client identifier from request
 * @param request - Next.js request object
 * @returns Client identifier (IP address or user ID)
 */
function getClientId(request: NextRequest): string {
  // Try to get IP from various headers (for proxied requests)
  const forwardedFor = request.headers.get('x-forwarded-for')
  const realIp = request.headers.get('x-real-ip')
  const cfConnectingIp = request.headers.get('cf-connecting-ip')

  if (forwardedFor) {
    // x-forwarded-for can contain multiple IPs, take the first one
    return forwardedFor.split(',')[0].trim()
  }

  if (realIp) {
    return realIp
  }

  if (cfConnectingIp) {
    return cfConnectingIp
  }

  // Fallback to a default identifier
  return 'unknown'
}

/**
 * Rate limit check
 * @param request - Next.js request object
 * @param maxRequests - Maximum requests allowed in the window
 * @param windowMs - Time window in milliseconds
 * @returns Object with allowed status and remaining requests
 */
export function rateLimit(
  request: NextRequest,
  maxRequests: number = 100,
  windowMs: number = 15 * 60 * 1000 // 15 minutes default
): { allowed: boolean; remaining: number; resetTime: number } {
  const clientId = getClientId(request)
  const now = Date.now()

  // Get or create rate limit record
  let record = rateLimitMap.get(clientId)

  // If no record or window expired, create new record
  if (!record || now > record.resetTime) {
    record = {
      count: 1,
      resetTime: now + windowMs,
    }
    rateLimitMap.set(clientId, record)
    return {
      allowed: true,
      remaining: maxRequests - 1,
      resetTime: record.resetTime,
    }
  }

  // Check if limit exceeded
  if (record.count >= maxRequests) {
    return {
      allowed: false,
      remaining: 0,
      resetTime: record.resetTime,
    }
  }

  // Increment count
  record.count++
  return {
    allowed: true,
    remaining: maxRequests - record.count,
    resetTime: record.resetTime,
  }
}

/**
 * Rate limit middleware wrapper
 * @param handler - Route handler function
 * @param maxRequests - Maximum requests allowed
 * @param windowMs - Time window in milliseconds
 * @returns Wrapped handler with rate limiting
 */
export function withRateLimit(
  handler: (request: NextRequest) => Promise<NextResponse>,
  maxRequests: number = 100,
  windowMs: number = 15 * 60 * 1000
) {
  return async (request: NextRequest) => {
    const limitResult = rateLimit(request, maxRequests, windowMs)

    if (!limitResult.allowed) {
      return NextResponse.json(
        {
          success: false,
          error: 'Rate limit exceeded',
          message: `Too many requests. Please try again after ${new Date(
            limitResult.resetTime
          ).toISOString()}`,
          resetTime: limitResult.resetTime,
        },
        {
          status: 429,
          headers: {
            'X-RateLimit-Limit': maxRequests.toString(),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': limitResult.resetTime.toString(),
            'Retry-After': Math.ceil(
              (limitResult.resetTime - Date.now()) / 1000
            ).toString(),
          },
        }
      )
    }

    // Add rate limit headers to response
    const response = await handler(request)
    response.headers.set('X-RateLimit-Limit', maxRequests.toString())
    response.headers.set(
      'X-RateLimit-Remaining',
      limitResult.remaining.toString()
    )
    response.headers.set('X-RateLimit-Reset', limitResult.resetTime.toString())

    return response
  }
}

/**
 * Combined authentication and rate limiting middleware
 * @param handler - Route handler function
 * @param options - Configuration options
 * @returns Wrapped handler with auth and rate limiting
 */
export function withAuthAndRateLimit(
  handler: (request: NextRequest, user: any) => Promise<NextResponse>,
  options: {
    requireAuth?: boolean
    requireAdmin?: boolean
    maxRequests?: number
    windowMs?: number
  } = {}
) {
  const {
    requireAuth: needsAuth = false,
    requireAdmin: needsAdmin = false,
    maxRequests = 100,
    windowMs = 15 * 60 * 1000,
  } = options

  return withRateLimit(
    async (request: NextRequest) => {
      // Handle authentication if required
      if (needsAuth || needsAdmin) {
        const token = request.headers.get('Authorization')

        if (!token) {
          return NextResponse.json(
            { success: false, error: 'Unauthorized - Missing token' },
            { status: 401 }
          )
        }

        // Import auth functions dynamically to avoid circular dependencies
        const { validateToken, checkAdminRole } = await import('./auth')
        const user = await validateToken(token)

        if (!user) {
          return NextResponse.json(
            { success: false, error: 'Unauthorized - Invalid token' },
            { status: 401 }
          )
        }

        if (needsAdmin && !checkAdminRole(user)) {
          return NextResponse.json(
            { success: false, error: 'Forbidden - Admin access required' },
            { status: 403 }
          )
        }

        return handler(request, user)
      }

      return handler(request, null)
    },
    maxRequests,
    windowMs
  )
}
