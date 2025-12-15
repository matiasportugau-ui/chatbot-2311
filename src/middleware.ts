import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { auth } from '@/lib/auth/auth.config'

/**
 * Middleware to protect routes and handle authentication
 */
export default auth((req) => {
  const { pathname } = req.nextUrl
  const isAuthenticated = !!req.auth

  // Define public routes that don't require authentication
  const publicRoutes = [
    '/',
    '/login',
    '/api/health',
    '/api/auth'
  ]

  // Check if the current path is public
  const isPublicRoute = publicRoutes.some(route => {
    if (route === '/') return pathname === '/'
    return pathname.startsWith(route)
  })

  // Allow public routes
  if (isPublicRoute) {
    // Redirect authenticated users away from login page
    if (pathname === '/login' && isAuthenticated) {
      return NextResponse.redirect(new URL('/crm', req.url))
    }
    return NextResponse.next()
  }

  // Protect all /crm routes
  if (pathname.startsWith('/crm')) {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      const loginUrl = new URL('/login', req.url)
      loginUrl.searchParams.set('callbackUrl', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  // Protect /api routes (except /api/auth and /api/health)
  if (pathname.startsWith('/api')) {
    if (!isAuthenticated && !pathname.startsWith('/api/auth') && !pathname.startsWith('/api/health')) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }
  }

  return NextResponse.next()
})

/**
 * Matcher configuration for middleware
 * Only run middleware on specific paths
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.jpg$|.*\\.jpeg$|.*\\.svg$|.*\\.gif$).*)'
  ]
}
