import { NextRequest, NextResponse } from 'next/server'

// Simple in-memory rate limiting map
// Note: In serverless environments, this memory is ephemeral and not shared across instances.
// For robust rate limiting, use Redis (e.g., Upstash).
const rateLimitMap = new Map<string, { count: number, resetTime: number }>()

export function withRateLimit(handler: (req: NextRequest) => Promise<NextResponse>, limit: number, windowMs: number) {
    return async (req: NextRequest) => {
        const ip = req.headers.get('x-forwarded-for') || 'unknown'

        // Prune expired entries cleanup (probability based to avoid overhead)
        if (Math.random() < 0.05) {
            const now = Date.now()
            for (const [key, value] of Array.from(rateLimitMap.entries())) {
                if (now > value.resetTime) {
                    rateLimitMap.delete(key)
                }
            }
        }

        const now = Date.now()
        const limitData = rateLimitMap.get(ip)

        if (limitData && now < limitData.resetTime) {
            if (limitData.count >= limit) {
                return NextResponse.json({ error: 'Too Many Requests' }, { status: 429 })
            }
            limitData.count++
        } else {
            rateLimitMap.set(ip, { count: 1, resetTime: now + windowMs })
        }

        return handler(req)
    }
}
