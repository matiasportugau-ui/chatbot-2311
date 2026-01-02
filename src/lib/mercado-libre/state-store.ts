import { connectDB } from '@/lib/mongodb'
import crypto from 'crypto'
import { MercadoLibreAuthState } from './types'

const COLLECTION = 'mercado_libre_auth_state'
const EXPIRATION_MS = 15 * 60 * 1000 // 15 minutes

export async function createAuthState(
  options: { codeVerifier?: string; returnTo?: string } = {}
) {
  const state = crypto.randomBytes(32).toString('hex')
  const createdAt = new Date()
  const expiresAt = new Date(createdAt.getTime() + EXPIRATION_MS)

  const record: MercadoLibreAuthState = {
    state,
    codeVerifier: options.codeVerifier,
    returnTo: options.returnTo,
    createdAt,
    expiresAt,
  }

  const db = await connectDB()
  await db.collection<MercadoLibreAuthState>(COLLECTION).insertOne(record)

  return record
}

export async function consumeAuthState(
  state: string
): Promise<MercadoLibreAuthState | null> {
  if (!state) return null

  const db = await connectDB()
  const result = await db
    .collection<MercadoLibreAuthState>(COLLECTION)
    .findOneAndDelete({ state })

  // findOneAndDelete returns ModifyResult<T> with value property
  // Type assertion needed because MongoDB types may vary
  const authState =
    result && typeof result === 'object' && 'value' in result
      ? (result.value as MercadoLibreAuthState | null)
      : null
  if (!authState) {
    return null
  }

  if (authState.expiresAt.getTime() < Date.now()) {
    return null
  }

  return authState
}

// Convenience aliases for client.ts
export async function saveState(
  state: string,
  data: { returnTo?: string; codeVerifier?: string }
): Promise<void> {
  const createdAt = new Date()
  const expiresAt = new Date(createdAt.getTime() + EXPIRATION_MS)

  const record: MercadoLibreAuthState = {
    state,
    codeVerifier: data.codeVerifier,
    returnTo: data.returnTo,
    createdAt,
    expiresAt,
  }

  const db = await connectDB()
  await db.collection<MercadoLibreAuthState>(COLLECTION).insertOne(record)
}

export async function getState(
  state: string
): Promise<{ returnTo?: string; codeVerifier?: string } | null> {
  if (!state) return null

  const db = await connectDB()
  const authState = await db
    .collection<MercadoLibreAuthState>(COLLECTION)
    .findOne({ state })

  if (!authState) {
    return null
  }

  if (authState.expiresAt.getTime() < Date.now()) {
    return null
  }

  return {
    returnTo: authState.returnTo,
    codeVerifier: authState.codeVerifier,
  }
}

export async function clearState(state: string): Promise<void> {
  if (!state) return

  const db = await connectDB()
  await db.collection<MercadoLibreAuthState>(COLLECTION).deleteOne({ state })
}
