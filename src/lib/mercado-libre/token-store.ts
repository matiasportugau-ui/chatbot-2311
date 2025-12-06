import { ObjectId } from 'mongodb'
import { connectDB } from '@/lib/mongodb'
import { MercadoLibreGrant } from './types'

const COLLECTION = 'mercado_libre_grants'

export async function getActiveGrant(): Promise<MercadoLibreGrant | null> {
  const db = await connectDB()
  const grant = await db
    .collection<MercadoLibreGrant>(COLLECTION)
    .find({ sellerId: { $exists: true } })
    .sort({ updatedAt: -1 })
    .limit(1)
    .next()

  return grant || null
}

export async function saveGrant(grant: Omit<MercadoLibreGrant, '_id' | 'createdAt' | 'updatedAt'>) {
  const db = await connectDB()
  const now = new Date()

  await db.collection<MercadoLibreGrant>(COLLECTION).updateOne(
    { sellerId: grant.sellerId },
    {
      $set: {
        accessToken: grant.accessToken,
        refreshToken: grant.refreshToken,
        scope: grant.scope,
        expiresAt: grant.expiresAt,
        userId: grant.userId,
        updatedAt: now
      },
      $setOnInsert: {
        createdAt: now,
        sellerId: grant.sellerId
      }
    },
    { upsert: true }
  )

}

export function isGrantExpired(grant: MercadoLibreGrant): boolean {
  return grant.expiresAt.getTime() <= Date.now()
}

export async function clearGrant(grantId: ObjectId) {
  const db = await connectDB()
  await db.collection<MercadoLibreGrant>(COLLECTION).deleteOne({ _id: grantId })
}

