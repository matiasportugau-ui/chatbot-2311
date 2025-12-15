import crypto from 'node:crypto';
import { getMercadoLibreConfig } from './config';
import { createAuthState, consumeAuthState } from './state-store';
import { getActiveGrant, saveGrant, isGrantExpired } from './token-store';
import { OAuthTokenResponse } from './types';

export interface AuthResult {
    url: string
}

export interface CallbackResult {
    redirectTo: string
    tokens?: OAuthTokenResponse
}

/**
 * Generates PKCE code verifier and challenge
 */
function generatePKCE() {
  const codeVerifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto
    .createHash('sha256')
    .update(codeVerifier)
    .digest('base64url');

  return { codeVerifier, codeChallenge: challenge };
}

/**
 * Starts the OAuth authorization flow
 */
export async function startAuthorization(returnTo?: string): Promise<AuthResult> {
    const config = getMercadoLibreConfig();

    // Generate state and optionally PKCE
    let codeVerifier: string | undefined;
    let codeChallenge: string | undefined;

    if (config.pkceEnabled) {
      const pkce = generatePKCE();
      codeVerifier = pkce.codeVerifier;
      codeChallenge = pkce.codeChallenge;
    }

    // Create and store auth state
    const authState = await createAuthState({ codeVerifier, returnTo });

    // Build authorization URL
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: config.appId,
      redirect_uri: config.redirectUri,
      state: authState.state,
    });

    if (codeChallenge) {
      params.append('code_challenge', codeChallenge);
      params.append('code_challenge_method', 'S256');
    }

    const authUrl = `${config.authBaseUrl}/authorization?${params.toString()}`;

    return { url: authUrl };
}

/**
 * Handles the OAuth callback and exchanges code for tokens
 */
export async function handleAuthorizationCallback(code: string, state: string): Promise<CallbackResult> {
    const config = getMercadoLibreConfig();

    // Verify and consume state
    const authState = await consumeAuthState(state);
    if (!authState) {
      throw new Error('Invalid or expired state parameter');
    }

    // Exchange authorization code for tokens
    const tokenParams: any = {
      grant_type: 'authorization_code',
      client_id: config.appId,
      client_secret: config.clientSecret,
      code,
      redirect_uri: config.redirectUri,
    };

    if (authState.codeVerifier) {
      tokenParams.code_verifier = authState.codeVerifier;
    }

    const response = await fetch(`${config.apiBaseUrl}/oauth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(tokenParams),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Token exchange failed: ${response.statusText} - ${errorText}`);
    }

    const tokens: OAuthTokenResponse = await response.json();

    // Save tokens to database
    const expiresAt = new Date(Date.now() + tokens.expires_in * 1000);
    await saveGrant({
      sellerId: config.sellerId,
      userId: tokens.user_id,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      scope: tokens.scope.split(' '),
      expiresAt,
    });

    return {
      redirectTo: authState.returnTo || '/dashboard',
      tokens,
    };
}

/**
 * Gets the current grant status
 */
export async function getGrantStatus(): Promise<any> {
    const grant = await getActiveGrant();

    if (!grant) {
      return { status: 'not_granted', message: 'No active grant found' };
    }

    const expired = isGrantExpired(grant);

    if (expired) {
      return {
        status: 'expired',
        message: 'Grant expired',
        expiresAt: grant.expiresAt,
      };
    }

    return {
      status: 'active',
      userId: grant.userId,
      sellerId: grant.sellerId,
      expiresAt: grant.expiresAt,
      scope: grant.scope,
    };
}

/**
 * Refreshes the access token using the refresh token
 */
export async function refreshTokens(): Promise<OAuthTokenResponse> {
    const config = getMercadoLibreConfig();
    const grant = await getActiveGrant();

    if (!grant?.refreshToken) {
      throw new Error('No refresh token available');
    }

    const params = new URLSearchParams({
      grant_type: 'refresh_token',
      client_id: config.appId,
      client_secret: config.clientSecret,
      refresh_token: grant.refreshToken,
    });

    const response = await fetch(`${config.apiBaseUrl}/oauth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Token refresh failed: ${response.statusText} - ${errorText}`);
    }

    const tokens: OAuthTokenResponse = await response.json();

    // Update stored tokens
    const expiresAt = new Date(Date.now() + tokens.expires_in * 1000);
    await saveGrant({
      sellerId: config.sellerId,
      userId: tokens.user_id,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      scope: tokens.scope.split(' '),
      expiresAt,
    });

    return tokens;
}

/**
 * Gets a valid access token, refreshing if necessary
 */
export async function getValidAccessToken(): Promise<string> {
    const grant = await getActiveGrant();

    if (!grant) {
      throw new Error('No active grant. Please authorize the application first.');
    }

    // Check if token is expired or about to expire (within 5 minutes)
    const expiryBuffer = 5 * 60 * 1000; // 5 minutes
    const willExpireSoon = grant.expiresAt.getTime() - Date.now() < expiryBuffer;

    if (willExpireSoon) {
      console.log('Access token expired or expiring soon, refreshing...');
      const tokens = await refreshTokens();
      return tokens.access_token;
    }

    return grant.accessToken;
}
