import { Db, MongoClient } from 'mongodb'

let client: MongoClient | null = null
let db: Db | null = null

/**
 * Validates MongoDB connection string format
 * @param uri - MongoDB connection string
 * @returns true if valid, throws error if invalid
 */
export function validateMongoDBURI(uri: string): boolean {
  if (!uri || typeof uri !== 'string') {
    throw new Error('MongoDB connection string is required')
  }

  const trimmedUri = uri.trim()

  if (
    !trimmedUri.startsWith('mongodb://') &&
    !trimmedUri.startsWith('mongodb+srv://')
  ) {
    throw new Error(
      'MongoDB connection strings must begin with "mongodb://" or "mongodb+srv://"'
    )
  }

  return true
}

/**
 * Extracts database name from MongoDB URI or returns default
 * @param uri - MongoDB connection string
 * @param defaultDb - Default database name
 * @returns Database name
 */
function extractDatabaseName(
  uri: string,
  defaultDb: string = 'bmc-cotizaciones'
): string {
  try {
    // Try to extract database name from URI
    const url = new URL(uri)
    const pathname = url.pathname
    if (pathname && pathname.length > 1) {
      // Remove leading slash
      return pathname.substring(1)
    }
  } catch (error) {
    // If URL parsing fails, use default
    console.warn(
      'Could not parse database name from URI, using default:',
      defaultDb
    )
  }
  return defaultDb
}

export async function connectDB(): Promise<Db> {
  if (db) {
    return db
  }

  const uri =
    process.env.MONGODB_URI || 'mongodb://localhost:27017/bmc-cotizaciones'

  // Validate connection string format
  try {
    validateMongoDBURI(uri)
  } catch (validationError: any) {
    console.error(
      '❌ Invalid MongoDB connection string:',
      validationError.message
    )
    throw new Error(
      `MongoDB connection string validation failed: ${validationError.message}`
    )
  }

  // Extract database name from URI or use default
  const databaseName = extractDatabaseName(uri, 'bmc-cotizaciones')

  try {
    client = new MongoClient(uri)
    await client.connect()
    db = client.db(databaseName)
    console.log(
      `✅ MongoDB conectado exitosamente a la base de datos: ${databaseName}`
    )
    return db
  } catch (error: any) {
    console.error('❌ Error conectando a MongoDB:', error.message || error)

    // Provide more helpful error messages
    if (error.message?.includes('authentication failed')) {
      throw new Error(
        'MongoDB authentication failed. Please check your username and password in the connection string.'
      )
    } else if (
      error.message?.includes('ENOTFOUND') ||
      error.message?.includes('getaddrinfo')
    ) {
      throw new Error(
        'MongoDB host not found. Please check your connection string and network access settings.'
      )
    } else if (error.message?.includes('timeout')) {
      throw new Error(
        'MongoDB connection timeout. Please check your network connection and firewall settings.'
      )
    } else if (error.message?.includes('SRV')) {
      throw new Error(
        'MongoDB SRV connection failed. Please verify your mongodb+srv:// connection string is correct.'
      )
    }

    throw new Error(
      `Failed to connect to MongoDB: ${error.message || 'Unknown error'}`
    )
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
