import { MongoClient, Db } from 'mongodb'

let client: MongoClient
let db: Db

export async function connectToDatabase() {
  if (client && db) {
    return { client, db }
  }

  if (!process.env.MONGODB_URI) {
    throw new Error('MONGODB_URI is not defined in environment variables')
  }

  try {
    client = new MongoClient(process.env.MONGODB_URI, {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    })

    await client.connect()
    db = client.db('whatsapp_quotes')
    
    console.log('Connected to MongoDB successfully')
    return { client, db }
  } catch (error) {
    console.error('Error connecting to MongoDB:', error)
    throw error
  }
}

export async function getDatabase() {
  if (!db) {
    await connectToDatabase()
  }
  return db
}

export async function closeConnection() {
  if (client) {
    await client.close()
    console.log('MongoDB connection closed')
  }
}
