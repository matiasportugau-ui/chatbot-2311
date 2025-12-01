/**
 * Mercado Libre OAuth Client
 * Handles authorization flow and token management for Mercado Libre API
 */

import { connectDB } from '../mongodb'

const MELI_API_BASE = 'https://api.mercadolibre.com'
const MELI_AUTH_URL = 'https://auth.mercadolibre.com.uy/authorization'
const MELI_TOKEN_URL = 'https://api.mercadolibre.com/oauth/token'

interface MeliTokens {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
  scope: string
  user_id: number
}

interface MeliGrant {
  userId: number
  access_token: string
  refresh_token: string
  expires_at: Date
  created_at: Date
  updated_at: Date
}

interface GrantStatus {
  connected: boolean
  userId?: number
  expiresAt?: Date
  needsRefresh?: boolean
}

// In-memory token cache (for single-instance deployments)
let cachedTokens: MeliTokens | null = null
let tokenExpiresAt: number = 0

/**
 * Get Mercado Libre configuration from environment
 */
function getConfig() {
  const appId = process.env.MERCADO_LIBRE_APP_ID
  const clientSecret = process.env.MERCADO_LIBRE_CLIENT_SECRET
  const redirectUri = process.env.MERCADO_LIBRE_REDIRECT_URI || 
    'http://localhost:3000/api/mercado-libre/auth/callback'
  const sellerId = process.env.MERCADO_LIBRE_SELLER_ID

  return { appId, clientSecret, redirectUri, sellerId }
}

/**
 * Start the OAuth authorization flow
 * @param returnTo - Optional URL to redirect after auth
 * @returns Object with authorization URL
 */
export async function startAuthorization(returnTo?: string): Promise<{ authUrl: string }> {
  const { appId, redirectUri } = getConfig()
  
  if (!appId) {
    throw new Error('MERCADO_LIBRE_APP_ID is not configured')
  }

  // Generate state for CSRF protection
  const state = Buffer.from(
    JSON.stringify({ returnTo: returnTo || '/dashboard', timestamp: Date.now() })
  ).toString('base64')

  // Store state for validation in callback
  try {
    const db = await connectDB()
    await db.collection('meli_auth_states').insertOne({
      state,
      created_at: new Date(),
      expires_at: new Date(Date.now() + 10 * 60 * 1000), // 10 minutes
    })
  } catch (error) {
    console.warn('Could not store auth state in MongoDB:', error)
    // Continue anyway - state validation will be skipped
  }

  const authUrl = new URL(MELI_AUTH_URL)
  authUrl.searchParams.set('response_type', 'code')
  authUrl.searchParams.set('client_id', appId)
  authUrl.searchParams.set('redirect_uri', redirectUri)
  authUrl.searchParams.set('state', state)

  return { authUrl: authUrl.toString() }
}

/**
 * Handle the OAuth callback after user authorization
 * @param code - Authorization code from Mercado Libre
 * @param state - State parameter for CSRF validation
 * @returns Object with redirect path
 */
export async function handleAuthorizationCallback(
  code: string,
  state: string
): Promise<{ redirectTo: string }> {
  const { appId, clientSecret, redirectUri } = getConfig()

  if (!appId || !clientSecret) {
    throw new Error('Mercado Libre credentials are not configured')
  }

  // Validate state (optional - depends on MongoDB availability)
  let returnTo = '/dashboard'
  try {
    const decodedState = JSON.parse(Buffer.from(state, 'base64').toString('utf-8'))
    returnTo = decodedState.returnTo || '/dashboard'
  } catch {
    // Invalid state format, use default redirect
  }

  // Exchange code for tokens
  const tokenResponse = await fetch(MELI_TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: appId,
      client_secret: clientSecret,
      code,
      redirect_uri: redirectUri,
    }),
  })

  if (!tokenResponse.ok) {
    const error = await tokenResponse.text()
    throw new Error(`Failed to exchange code for tokens: ${error}`)
  }

  const tokens: MeliTokens = await tokenResponse.json()

  // Store tokens
  await storeTokens(tokens)

  return { redirectTo: `${returnTo}?meli_connected=true` }
}

/**
 * Store tokens in database and cache
 */
async function storeTokens(tokens: MeliTokens): Promise<void> {
  // Update cache
  cachedTokens = tokens
  tokenExpiresAt = Date.now() + (tokens.expires_in * 1000)

  // Store in database
  try {
    const db = await connectDB()
    const grant: MeliGrant = {
      userId: tokens.user_id,
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
      expires_at: new Date(tokenExpiresAt),
      created_at: new Date(),
      updated_at: new Date(),
    }

    await db.collection('mercado_libre_grants').updateOne(
      { userId: tokens.user_id },
      { $set: grant },
      { upsert: true }
    )
  } catch (error) {
    console.warn('Could not store tokens in MongoDB:', error)
    // Tokens are still in cache, continue
  }
}

/**
 * Get stored tokens (from cache or database)
 */
async function getStoredTokens(): Promise<MeliTokens | null> {
  // Check cache first
  if (cachedTokens && Date.now() < tokenExpiresAt) {
    return cachedTokens
  }

  // Try to get from database
  try {
    const db = await connectDB()
    const grant = await db.collection('mercado_libre_grants')
      .findOne({}, { sort: { updated_at: -1 } })

    if (grant) {
      cachedTokens = {
        access_token: grant.access_token,
        refresh_token: grant.refresh_token,
        expires_in: Math.floor((new Date(grant.expires_at).getTime() - Date.now()) / 1000),
        token_type: 'Bearer',
        scope: '',
        user_id: grant.userId,
      }
      tokenExpiresAt = new Date(grant.expires_at).getTime()
      return cachedTokens
    }
  } catch (error) {
    console.warn('Could not get tokens from MongoDB:', error)
  }

  return null
}

/**
 * Get current grant status
 */
export async function getGrantStatus(): Promise<GrantStatus> {
  const tokens = await getStoredTokens()

  if (!tokens) {
    return { connected: false }
  }

  const expiresAt = new Date(tokenExpiresAt)
  const needsRefresh = Date.now() > tokenExpiresAt - 5 * 60 * 1000 // 5 minutes before expiry

  return {
    connected: true,
    userId: tokens.user_id,
    expiresAt,
    needsRefresh,
  }
}

/**
 * Refresh access tokens
 */
export async function refreshTokens(): Promise<MeliTokens> {
  const { appId, clientSecret } = getConfig()
  const currentTokens = await getStoredTokens()

  if (!currentTokens?.refresh_token) {
    throw new Error('No refresh token available. Please re-authorize.')
  }

  if (!appId || !clientSecret) {
    throw new Error('Mercado Libre credentials are not configured')
  }

  const response = await fetch(MELI_TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      client_id: appId,
      client_secret: clientSecret,
      refresh_token: currentTokens.refresh_token,
    }),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to refresh tokens: ${error}`)
  }

  const tokens: MeliTokens = await response.json()
  await storeTokens(tokens)

  return tokens
}

/**
 * Get valid access token (refreshing if needed)
 */
export async function getAccessToken(): Promise<string> {
  const status = await getGrantStatus()

  if (!status.connected) {
    throw new Error('Mercado Libre is not connected. Please authorize first.')
  }

  if (status.needsRefresh) {
    const tokens = await refreshTokens()
    return tokens.access_token
  }

  const tokens = await getStoredTokens()
  if (!tokens) {
    throw new Error('No tokens available')
  }

  return tokens.access_token
}

/**
 * Make an authenticated request to Mercado Libre API
 */
export async function meliRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const accessToken = await getAccessToken()
  
  const url = endpoint.startsWith('http') ? endpoint : `${MELI_API_BASE}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${accessToken}`,
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Mercado Libre API error (${response.status}): ${error}`)
  }

  return response.json()
}
