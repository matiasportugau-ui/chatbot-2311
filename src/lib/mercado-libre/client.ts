import crypto from 'crypto'
import { ObjectId } from 'mongodb'
import { consumeAuthState, createAuthState } from './state-store'
import {
  clearGrant,
  getActiveGrant,
  isGrantExpired,
  saveGrant,
} from './token-store'
import {
  MercadoLibreApiRequestOptions,
  MercadoLibreConfig,
  MercadoLibreGrant,
  OAuthTokenResponse,
} from './types'
import { validateMercadoLibreConfig } from './config-validator'

const TOKEN_ENDPOINT = '/oauth/token'
const AUTHORIZATION_ENDPOINT = '/authorization'
const DEFAULT_SCOPES = ['offline_access', 'read', 'write']

let cachedConfig: MercadoLibreConfig | null = null

/**
 * Logger estructurado para operaciones de MercadoLibre
 * No expone información sensible como tokens completos
 */
function logMercadoLibre(
  level: 'info' | 'warn' | 'error',
  message: string,
  context?: Record<string, any>
) {
  const logContext = {
    service: 'mercadolibre',
    timestamp: new Date().toISOString(),
    ...context,
  }

  // Sanitizar contexto para no exponer información sensible
  if (logContext.accessToken) {
    logContext.accessToken = `${logContext.accessToken.substring(0, 8)}...`
  }
  if (logContext.refreshToken) {
    logContext.refreshToken = `${logContext.refreshToken.substring(0, 8)}...`
  }
  if (logContext.clientSecret) {
    logContext.clientSecret = '***'
  }

  const logMessage = `[MercadoLibre] ${message}`
  
  switch (level) {
    case 'error':
      console.error(logMessage, JSON.stringify(logContext, null, 2))
      break
    case 'warn':
      console.warn(logMessage, JSON.stringify(logContext, null, 2))
      break
    case 'info':
      console.log(logMessage, JSON.stringify(logContext, null, 2))
      break
  }
}

function loadConfig(): MercadoLibreConfig {
  if (cachedConfig) {
    return cachedConfig
  }

  // Validar configuración usando el validador
  const validation = validateMercadoLibreConfig()
  if (!validation.isValid) {
    const errorMessages = validation.errors.join('; ')
    throw new Error(
      `Configuración de MercadoLibre inválida: ${errorMessages}`
    )
  }

  cachedConfig = {
    appId: process.env.MERCADO_LIBRE_APP_ID!,
    clientSecret: process.env.MERCADO_LIBRE_CLIENT_SECRET!,
    redirectUri: process.env.MERCADO_LIBRE_REDIRECT_URI!,
    sellerId: process.env.MERCADO_LIBRE_SELLER_ID!,
    webhookSecret: process.env.MERCADO_LIBRE_WEBHOOK_SECRET || '',
    authBaseUrl:
      process.env.MERCADO_LIBRE_AUTH_URL || 'https://auth.mercadolibre.com.ar',
    apiBaseUrl:
      process.env.MERCADO_LIBRE_API_URL || 'https://api.mercadolibre.com',
    scopes: (process.env.MERCADO_LIBRE_SCOPES || DEFAULT_SCOPES.join(' '))
      .split(/[ ,]+/)
      .filter(Boolean),
    pkceEnabled:
      (process.env.MERCADO_LIBRE_PKCE_ENABLED || 'true').toLowerCase() !==
      'false',
  }

  return cachedConfig
}

function base64URLEncode(buffer: Buffer) {
  return buffer
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
}

function sha256(buffer: Buffer) {
  return crypto.createHash('sha256').update(buffer).digest()
}

function generateCodeVerifier(): string {
  return base64URLEncode(crypto.randomBytes(32))
}

function calculateCodeChallenge(codeVerifier: string): string {
  return base64URLEncode(sha256(Buffer.from(codeVerifier)))
}

export async function startAuthorization(returnTo?: string) {
  const config = loadConfig()
  let codeVerifier: string | undefined
  let codeChallenge: string | undefined

  if (config.pkceEnabled) {
    codeVerifier = generateCodeVerifier()
    codeChallenge = calculateCodeChallenge(codeVerifier)
  }

  const authState = await createAuthState({ codeVerifier, returnTo })

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: config.appId,
    redirect_uri: config.redirectUri,
    state: authState.state,
    scope: config.scopes.join(' '),
  })

  if (codeChallenge) {
    params.append('code_challenge', codeChallenge)
    params.append('code_challenge_method', 'S256')
  }

  const authorizationUrl = `${
    config.authBaseUrl
  }${AUTHORIZATION_ENDPOINT}?${params.toString()}`

  return {
    authorizationUrl,
    state: authState.state,
    expiresAt: authState.expiresAt,
  }
}

async function requestToken(body: Record<string, string>) {
  const config = loadConfig()
  const url = `${config.apiBaseUrl}${TOKEN_ENDPOINT}`
  const grantType = body.grant_type

  logMercadoLibre('info', `Solicitando token (grant_type: ${grantType})`, {
    endpoint: TOKEN_ENDPOINT,
    grantType,
    sellerId: config.sellerId,
  })

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        Accept: 'application/json',
      },
      body: new URLSearchParams(body),
    })

    const payload = await response.json().catch(() => ({}))

    if (!response.ok) {
      const errorMessage =
        payload?.error_description ||
        payload?.message ||
        `Mercado Libre token error (${response.status})`
      
      logMercadoLibre('error', 'Error al obtener token', {
        status: response.status,
        grantType,
        error: payload?.error,
        errorDescription: payload?.error_description,
        sellerId: config.sellerId,
      })

      const error = new Error(errorMessage)
      ;(error as any).details = payload
      throw error
    }

    logMercadoLibre('info', 'Token obtenido exitosamente', {
      grantType,
      expiresIn: payload.expires_in,
      userId: payload.user_id,
      sellerId: config.sellerId,
    })

    return payload as OAuthTokenResponse
  } catch (error) {
    if (error instanceof Error && (error as any).details) {
      // Ya loggeado arriba
      throw error
    }
    
    logMercadoLibre('error', 'Error de red al solicitar token', {
      grantType,
      error: error instanceof Error ? error.message : String(error),
      sellerId: config.sellerId,
    })
    throw error
  }
}

export async function handleAuthorizationCallback(code: string, state: string) {
  logMercadoLibre('info', 'Procesando callback de autorización', { state })

  const authState = await consumeAuthState(state)

  if (!authState) {
    logMercadoLibre('error', 'Estado de autorización inválido o expirado', {
      state,
    })
    throw new Error('Estado de autorización inválido o expirado')
  }

  const config = loadConfig()
  const body: Record<string, string> = {
    grant_type: 'authorization_code',
    client_id: config.appId,
    client_secret: config.clientSecret,
    code,
    redirect_uri: config.redirectUri,
  }

  if (authState.codeVerifier) {
    body.code_verifier = authState.codeVerifier
  }

  const tokens = await requestToken(body)
  await persistGrantFromTokens(tokens, config.sellerId)

  logMercadoLibre('info', 'Autorización completada exitosamente', {
    userId: tokens.user_id,
    sellerId: config.sellerId,
  })

  return {
    redirectTo: authState.returnTo || '/dashboard?meli=connected',
    tokens,
  }
}

export async function refreshTokens(grant?: MercadoLibreGrant) {
  const activeGrant = grant || (await getActiveGrant())

  if (!activeGrant) {
    logMercadoLibre('error', 'Intento de refrescar token sin grant activo')
    throw new Error('No existe un grant activo de Mercado Libre')
  }

  logMercadoLibre('info', 'Refrescando token de acceso', {
    sellerId: activeGrant.sellerId,
    userId: activeGrant.userId,
    expiresAt: activeGrant.expiresAt.toISOString(),
  })

  const config = loadConfig()

  const body: Record<string, string> = {
    grant_type: 'refresh_token',
    client_id: config.appId,
    client_secret: config.clientSecret,
    refresh_token: activeGrant.refreshToken,
  }

  try {
    const tokens = await requestToken(body)
    await persistGrantFromTokens(tokens, config.sellerId)

    logMercadoLibre('info', 'Token refrescado exitosamente', {
      sellerId: config.sellerId,
      userId: tokens.user_id,
      expiresIn: tokens.expires_in,
    })

    return tokens
  } catch (error) {
    logMercadoLibre('error', 'Error al refrescar token', {
      sellerId: config.sellerId,
      error: error instanceof Error ? error.message : String(error),
    })
    throw error
  }
}

async function persistGrantFromTokens(
  tokens: OAuthTokenResponse,
  sellerId: string
) {
  const expiresAt = new Date(
    Date.now() + Math.max(tokens.expires_in - 60, 60) * 1000
  )

  await saveGrant({
    sellerId,
    userId: tokens.user_id,
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    scope: tokens.scope.split(' '),
    expiresAt,
  })
}

export async function getValidAccessToken(): Promise<string> {
  let grant = await getActiveGrant()

  if (!grant) {
    logMercadoLibre('error', 'Intento de obtener token sin grant activo')
    throw new Error(
      'Mercado Libre no está conectado. Completa el flujo de autorización.'
    )
  }

  if (isGrantExpired(grant)) {
    logMercadoLibre('warn', 'Token expirado, refrescando', {
      sellerId: grant.sellerId,
      expiredAt: grant.expiresAt.toISOString(),
    })

    try {
      const tokens = await refreshTokens(grant)
      grant = {
        ...grant,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        scope: tokens.scope.split(' '),
        expiresAt: new Date(
          Date.now() + Math.max(tokens.expires_in - 60, 60) * 1000
        ),
        updatedAt: new Date(),
      }
    } catch (error) {
      logMercadoLibre('error', 'Error al refrescar token expirado', {
        sellerId: grant.sellerId,
        error: error instanceof Error ? error.message : String(error),
        errorDetails: (error as any)?.details,
      })

      if ((error as any)?.details?.error === 'invalid_grant' && grant._id) {
        logMercadoLibre('warn', 'Grant inválido, eliminando', {
          grantId: grant._id.toString(),
          sellerId: grant.sellerId,
        })
        await clearGrant(new ObjectId(grant._id))
      }
      throw error
    }
  }

  return grant.accessToken
}

export async function callMercadoLibreAPI<T = any>(
  options: MercadoLibreApiRequestOptions
): Promise<T> {
  const config = loadConfig()
  const method = options.method || 'GET'
  let path = options.path || ''

  if (!path.startsWith('/')) {
    path = `/${path}`
  }

  const query = new URLSearchParams()
  if (options.query) {
    Object.entries(options.query).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        query.append(key, String(value))
      }
    })
  }

  const url =
    query.size > 0
      ? `${config.apiBaseUrl}${path}?${query.toString()}`
      : `${config.apiBaseUrl}${path}`

  let token = await getValidAccessToken()

  const response = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  if (response.status === 401 && options.retryOnAuthError !== false) {
    logMercadoLibre('warn', 'Token no autorizado, refrescando y reintentando', {
      method,
      path,
      sellerId: config.sellerId,
    })

    await refreshTokens()
    token = await getValidAccessToken()

    return callMercadoLibreAPI<T>({
      ...options,
      retryOnAuthError: false,
    })
  }

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({}))
    const errorMessage =
      errorPayload?.message ||
      errorPayload?.error ||
      `Mercado Libre API error (${response.status})`

    logMercadoLibre('error', 'Error en llamada a API de MercadoLibre', {
      method,
      path,
      status: response.status,
      error: errorPayload?.error,
      message: errorPayload?.message,
      sellerId: config.sellerId,
    })

    const error = new Error(errorMessage)
    ;(error as any).details = errorPayload
    throw error
  }

  logMercadoLibre('info', 'Llamada a API exitosa', {
    method,
    path,
    status: response.status,
    sellerId: config.sellerId,
  })

  return (await response.json()) as T
}

export function getMercadoLibreConfig(): MercadoLibreConfig {
  return loadConfig()
}

export async function getGrantStatus() {
  const grant = await getActiveGrant()

  if (!grant) {
    return {
      connected: false,
    }
  }

  return {
    connected: true,
    expiresAt: grant.expiresAt,
    scope: grant.scope,
    sellerId: grant.sellerId,
    userId: grant.userId,
  }
}
