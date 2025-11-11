import { MongoClient, Db } from 'mongodb'

let client: MongoClient | null = null
let db: Db | null = null

export async function connectDB(): Promise<Db> {
  if (db) {
    return db
  }

  const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/bmc-cotizaciones'
  
  try {
    client = new MongoClient(uri)
    await client.connect()
    db = client.db('bmc-cotizaciones')
    console.log('✅ MongoDB conectado exitosamente')
    return db
  } catch (error) {
    console.error('❌ Error conectando a MongoDB:', error)
    throw error
  }
}

export async function disconnectDB(): Promise<void> {
  if (client) {
    await client.close()
    client = null
    db = null
    console.log('🔌 MongoDB desconectado')
  }
}

export function getDB(): Db {
  if (!db) {
    throw new Error('MongoDB no está conectado. Llama a connectDB() primero.')
  }
  return db
}

// Alias para compatibilidad
export function getDatabase(): Db {
  return getDB()
}