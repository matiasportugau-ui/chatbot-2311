export interface MercadoLibreConfig {
  appId: string
  clientSecret: string
  redirectUri: string
  sellerId: string
  webhookSecret: string
  authBaseUrl: string
  apiBaseUrl: string
  scopes: string[]
  pkceEnabled: boolean
}

export interface OAuthTokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  scope: string
  user_id: number
  refresh_token: string
}

import { ObjectId } from 'mongodb'

export interface MercadoLibreGrant {
  _id?: ObjectId
  sellerId: string
  userId: number
  accessToken: string
  refreshToken: string
  scope: string[]
  expiresAt: Date
  createdAt: Date
  updatedAt: Date
}

export interface MercadoLibreAuthState {
  state: string
  codeVerifier?: string
  returnTo?: string
  createdAt: Date
  expiresAt: Date
}

export interface MercadoLibreApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  path?: string
  query?: Record<string, string | number | undefined>
  body?: any
  headers?: Record<string, string>
  retryOnAuthError?: boolean
}

export interface MercadoLibreListing {
  id: string
  title: string
  price: number
  currency_id: string
  available_quantity: number
  status: string
  permalink: string
  [key: string]: any
}

export interface MercadoLibreOrder {
  id: number
  status: string
  date_created: string
  total_amount: number
  currency_id: string
  buyer: Record<string, any>
  seller: Record<string, any>
  shipping: Record<string, any>
  payments: any[]
  [key: string]: any
}

