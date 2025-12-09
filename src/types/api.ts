/**
 * API Rate Limits Configuration
 * Defines rate limiting rules for different API endpoints
 */

export interface RateLimitConfig {
  maxRequests: number
  windowMs: number
}

export interface RateLimits {
  DEFAULT: RateLimitConfig
  MERCADO_LIBRE: RateLimitConfig
  CHAT: RateLimitConfig
  WEBHOOK: RateLimitConfig
  EXPORT: RateLimitConfig
  SEARCH: RateLimitConfig
}

export const RATE_LIMITS: RateLimits = {
  DEFAULT: {
    maxRequests: 100,
    windowMs: 60 * 1000, // 1 minute
  },
  MERCADO_LIBRE: {
    maxRequests: 20,
    windowMs: 60 * 1000, // 1 minute
  },
  CHAT: {
    maxRequests: 30,
    windowMs: 60 * 1000, // 1 minute
  },
  WEBHOOK: {
    maxRequests: 50,
    windowMs: 60 * 1000, // 1 minute
  },
  EXPORT: {
    maxRequests: 10,
    windowMs: 60 * 1000, // 1 minute
  },
  SEARCH: {
    maxRequests: 20,
    windowMs: 60 * 1000, // 1 minute
  },
}


export interface ErrorResponse {
  success: boolean
  error: string
  message?: string
  code?: string
  details?: any
}

export interface SuccessResponse<T> {
  data: T
  success: boolean
  message?: string
}
