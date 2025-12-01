/**
 * Rate Limiting Middleware
 * Provides rate limiting for API routes using in-memory storage
 * In production, consider using Redis for distributed rate limiting
 */

import { NextRequest, NextResponse } from 'next/server'

type RequestHandler = (
  request: NextRequest,
  context?: any
) => Promise<NextResponse>

interface RateLimitEntry {
  count: number
  resetTime: number
}

// In-memory storage for rate limits
// Key: IP address or user identifier
const rateLimitStore = new Map<string, RateLimitEntry>()

// Cleanup old entries periodically
let lastCleanup = Date.now()
const CLEANUP_INTERVAL = 5 * 60 * 1000 // 5 minutes

function cleanupExpiredEntries(): void {
  const now = Date.now()
  if (now - lastCleanup < CLEANUP_INTERVAL) {
    return
  }

  lastCleanup = now
  const keysToDelete: string[] = []
  rateLimitStore.forEach((entry, key) => {
    if (now > entry.resetTime) {
      keysToDelete.push(key)
    }
  })
  keysToDelete.forEach(key => rateLimitStore.delete(key))
}

/**
 * Get client identifier from request
 * Uses IP address or user identifier for rate limiting
 */
function getClientIdentifier(request: NextRequest): string {
  // Try to get real IP from various headers
  const forwardedFor = request.headers.get('x-forwarded-for')
  if (forwardedFor) {
    // Get the first IP in the chain
    return forwardedFor.split(',')[0].trim()
  }

  const realIp = request.headers.get('x-real-ip')
  if (realIp) {
    return realIp
  }

  // Try to get user identifier from auth header
  const authHeader = request.headers.get('authorization')
  if (authHeader?.startsWith('Bearer ')) {
    // Use token prefix as identifier (first 32 chars)
    return `token:${authHeader.slice(7, 39)}`
  }

  // Fallback to a generic identifier
  return 'unknown'
}

/**
 * Check and update rate limit for a client
 * @param identifier - Client identifier
 * @param maxRequests - Maximum requests allowed in the window
 * @param windowMs - Time window in milliseconds
 * @returns Object with allowed status and remaining info
 */
function checkRateLimit(
  identifier: string,
  maxRequests: number,
  windowMs: number
): { allowed: boolean; remaining: number; resetTime: number } {
  cleanupExpiredEntries()

  const now = Date.now()
  const key = `${identifier}:${maxRequests}:${windowMs}`
  let entry = rateLimitStore.get(key)

  // Create new entry if none exists or if window has expired
  if (!entry || now > entry.resetTime) {
    entry = {
      count: 0,
      resetTime: now + windowMs,
    }
    rateLimitStore.set(key, entry)
  }

  // Check if limit exceeded
  if (entry.count >= maxRequests) {
    return {
      allowed: false,
      remaining: 0,
      resetTime: entry.resetTime,
    }
  }

  // Increment count
  entry.count++

  return {
    allowed: true,
    remaining: maxRequests - entry.count,
    resetTime: entry.resetTime,
  }
}

/**
 * Higher-order function to add rate limiting to a request handler
 * @param handler - The request handler to wrap
 * @param maxRequests - Maximum number of requests allowed in the time window (default: 100)
 * @param windowMs - Time window in milliseconds (default: 15 minutes)
 * @returns Wrapped handler with rate limiting
 */
export function withRateLimit(
  handler: RequestHandler,
  maxRequests: number = 100,
  windowMs: number = 15 * 60 * 1000
): RequestHandler {
  return async (request: NextRequest, context?: any): Promise<NextResponse> => {
    const clientId = getClientIdentifier(request)
    const result = checkRateLimit(clientId, maxRequests, windowMs)

    // Add rate limit headers to response
    const headers = {
      'X-RateLimit-Limit': maxRequests.toString(),
      'X-RateLimit-Remaining': result.remaining.toString(),
      'X-RateLimit-Reset': Math.ceil(result.resetTime / 1000).toString(),
    }

    if (!result.allowed) {
      const retryAfter = Math.ceil((result.resetTime - Date.now()) / 1000)
      return NextResponse.json(
        {
          success: false,
          error: 'Rate limit exceeded',
          message: `Too many requests. Please try again in ${retryAfter} seconds.`,
          retryAfter,
        },
        {
          status: 429,
          headers: {
            ...headers,
            'Retry-After': retryAfter.toString(),
          },
        }
      )
    }

    // Call the original handler
    const response = await handler(request, context)

    // Add rate limit headers to successful response
    for (const [key, value] of Object.entries(headers)) {
      response.headers.set(key, value)
    }

    return response
  }
}

/**
 * Create a custom rate limiter with specific settings
 * Useful for creating different rate limits for different endpoints
 */
export function createRateLimiter(
  maxRequests: number,
  windowMs: number
): (handler: RequestHandler) => RequestHandler {
  return (handler: RequestHandler) => withRateLimit(handler, maxRequests, windowMs)
}

// Pre-configured rate limiters for common use cases
export const strictRateLimit = createRateLimiter(10, 15 * 60 * 1000) // 10 requests per 15 min
export const normalRateLimit = createRateLimiter(100, 15 * 60 * 1000) // 100 requests per 15 min
export const lenientRateLimit = createRateLimiter(300, 15 * 60 * 1000) // 300 requests per 15 min
