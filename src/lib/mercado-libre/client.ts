import { getActiveGrant, saveGrant, isGrantExpired } from './token-store'
import { saveState, getState, clearState } from './state-store'
import { MercadoLibreGrant } from './types'

export interface AuthResult {
  url: string
}

export interface CallbackResult {
  redirectTo: string
  tokens?: any
}

const APP_ID = process.env.MERCADO_LIBRE_APP_ID!
const CLIENT_SECRET = process.env.MERCADO_LIBRE_CLIENT_SECRET!
const REDIRECT_URI = process.env.MERCADO_LIBRE_REDIRECT_URI!
const AUTH_URL = process.env.MERCADO_LIBRE_AUTH_URL || 'https://auth.mercadolibre.com.uy'
const API_URL = process.env.MERCADO_LIBRE_API_URL || 'https://api.mercadolibre.com'

export async function startAuthorization(returnTo?: string): Promise<AuthResult> {
  const state = crypto.randomUUID()
  await saveState(state, { returnTo: returnTo || '/' })

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: APP_ID,
    redirect_uri: REDIRECT_URI,
    state: state,
  })

  const authUrl = `${AUTH_URL}/authorization?${params.toString()}`
  return { url: authUrl }
}

export async function handleAuthorizationCallback(
  code: string,
  state: string
): Promise<CallbackResult> {
  // Verify state
  const stateData = await getState(state)
  if (!stateData) {
    throw new Error('Invalid or expired state')
  }
  await clearState(state)

  // Exchange code for tokens
  const tokenUrl = `${AUTH_URL}/oauth/token`
  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: APP_ID,
    client_secret: CLIENT_SECRET,
    code: code,
    redirect_uri: REDIRECT_URI,
  })

  const response = await fetch(tokenUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
    },
    body: body.toString(),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Token exchange failed: ${error}`)
  }

  const tokens = await response.json()

  // Get user info to get seller ID
  const userInfo = await fetch(`${API_URL}/users/me`, {
    headers: {
      'Authorization': `Bearer ${tokens.access_token}`,
    },
  })

  if (!userInfo.ok) {
    throw new Error('Failed to fetch user info')
  }

  const user = await userInfo.json()

  // Save grant to database
  await saveGrant({
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    scope: typeof tokens.scope === 'string' ? tokens.scope.split(' ') : tokens.scope,
    expiresAt: new Date(Date.now() + tokens.expires_in * 1000),
    sellerId: user.id.toString(),
    userId: typeof user.id === 'number' ? user.id : parseInt(user.id),
  })

  return {
    redirectTo: stateData.returnTo || '/',
    tokens,
  }
}

export async function getGrantStatus(): Promise<any> {
  const grant = await getActiveGrant()
  if (!grant) {
    return { status: 'no_grant' }
  }
  if (isGrantExpired(grant)) {
    return { status: 'expired', grant }
  }
  return { status: 'active', grant }
}

export async function refreshTokens(): Promise<any> {
  const grant = await getActiveGrant()
  if (!grant || !grant.refreshToken) {
    throw new Error('No refresh token available')
  }

  const tokenUrl = `${AUTH_URL}/oauth/token`
  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    client_id: APP_ID,
    client_secret: CLIENT_SECRET,
    refresh_token: grant.refreshToken,
  })

  const response = await fetch(tokenUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
    },
    body: body.toString(),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Token refresh failed: ${error}`)
  }

  const tokens = await response.json()

  // Update grant in database
  await saveGrant({
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    scope: typeof tokens.scope === 'string' ? tokens.scope.split(' ') : tokens.scope,
    expiresAt: new Date(Date.now() + tokens.expires_in * 1000),
    sellerId: grant.sellerId,
    userId: grant.userId,
  })

  return tokens
}

/**
 * Makes authenticated API calls to Mercado Libre
 */
export async function callMercadoLibreAPI<T = any>(options: {
  method?: string
  path: string
  query?: Record<string, any>
  body?: any
}): Promise<T> {
  const grant = await getActiveGrant()

  if (!grant) {
    throw new Error('No active grant found. Please authenticate first.')
  }

  // Check if token is expired and refresh if needed
  if (isGrantExpired(grant)) {
    await refreshTokens()
    // Get updated grant
    const updatedGrant = await getActiveGrant()
    if (!updatedGrant) {
      throw new Error('Failed to refresh token')
    }
  }

  // Refresh grant reference after potential refresh
  const currentGrant = await getActiveGrant()
  if (!currentGrant) {
    throw new Error('No active grant after refresh')
  }

  // Build URL with query params
  let url = `${API_URL}${options.path}`
  if (options.query) {
    const params = new URLSearchParams()
    Object.entries(options.query).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value))
      }
    })
    const queryString = params.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  const response = await fetch(url, {
    method: options.method || 'GET',
    headers: {
      'Authorization': `Bearer ${currentGrant.accessToken}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Mercado Libre API error: ${response.status} ${error}`)
  }

  return response.json()
}
