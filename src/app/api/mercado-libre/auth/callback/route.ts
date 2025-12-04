<<<<<<< Updated upstream
=======
import { validationErrorResponse } from '@/lib/api-response'
import { handleAuthorizationCallback } from '@/lib/mercado-libre/client'
import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
>>>>>>> Stashed changes
import { NextRequest, NextResponse } from 'next/server'
import { handleAuthorizationCallback } from '@/lib/mercado-libre/client'

function buildRedirectUrl(baseUrl: URL, target: string) {
  if (/^https?:\/\//.test(target)) {
    return target
  }
  return `${baseUrl.origin}${target.startsWith('/') ? target : `/${target}`}`
}

export async function GET(request: NextRequest) {
  const url = new URL(request.url)
  const code = url.searchParams.get('code')
  const state = url.searchParams.get('state')
  const errorParam = url.searchParams.get('error')
  const errorDescription = url.searchParams.get('error_description')

  const origin = request.headers.get('origin') || `${url.protocol}//${url.host}`
  const baseUrl = new URL(origin)

  if (errorParam) {
    const redirectTarget = `/dashboard?meli_error=${encodeURIComponent(errorDescription || errorParam)}`
    return NextResponse.redirect(buildRedirectUrl(baseUrl, redirectTarget))
  }

  if (!code || !state) {
<<<<<<< Updated upstream
    return NextResponse.json({ error: 'Missing code or state.' }, { status: 400 })
=======
    return validationErrorResponse(
      ['Missing code or state'],
      'OAuth callback requires code and state parameters'
    )
>>>>>>> Stashed changes
  }

  try {
    const { redirectTo } = await handleAuthorizationCallback(code, state)
    return NextResponse.redirect(buildRedirectUrl(baseUrl, redirectTo))
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown Mercado Libre auth error'
    console.error('Mercado Libre callback error:', error)
    const redirectTarget = `/dashboard?meli_error=${encodeURIComponent(message)}`
    return NextResponse.redirect(buildRedirectUrl(baseUrl, redirectTarget))
  }
}

