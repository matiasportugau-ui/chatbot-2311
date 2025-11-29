#!/usr/bin/env node
/**
 * MongoDB Index Creation Script
 * Creates indexes for optimal query performance
 *
 * Usage:
 *   node scripts/create-indexes.js
 *   MONGODB_URI=mongodb://localhost:27017/bmc-cotizaciones node scripts/create-indexes.js
 */

const { MongoClient } = require('mongodb')

async function createIndexes() {
  const uri =
    process.env.MONGODB_URI || 'mongodb://localhost:27017/bmc-cotizaciones'

  let client
  try {
    console.log('Connecting to MongoDB...')
    client = new MongoClient(uri)
    await client.connect()

    const db = client.db()
    console.log(`Connected to database: ${db.databaseName}`)

    // Conversations indexes
    console.log('\nCreating indexes for conversations collection...')
    const conversations = db.collection('conversations')
    await conversations.createIndex({ timestamp: -1 })
    console.log('  ✓ Created index on timestamp (descending)')
    await conversations.createIndex({ user_phone: 1 })
    console.log('  ✓ Created index on user_phone')
    await conversations.createIndex({ session_id: 1 })
    console.log('  ✓ Created index on session_id')
    await conversations.createIndex({ 'messages.timestamp': -1 })
    console.log('  ✓ Created index on messages.timestamp')

    // Text search index for conversations
    try {
      await conversations.createIndex({
        'messages.content': 'text',
        user_phone: 'text',
        intent: 'text',
      })
      console.log('  ✓ Created text search index')
    } catch (err) {
      console.log('  ⚠ Text search index may already exist or failed')
    }

    // Quotes indexes
    console.log('\nCreating indexes for quotes collection...')
    const quotes = db.collection('quotes')
    await quotes.createIndex({ timestamp: -1 })
    console.log('  ✓ Created index on timestamp (descending)')
    await quotes.createIndex({ estado: 1 })
    console.log('  ✓ Created index on estado')
    await quotes.createIndex({ cliente: 1 })
    console.log('  ✓ Created index on cliente')
    await quotes.createIndex({ telefono: 1 })
    console.log('  ✓ Created index on telefono')
    await quotes.createIndex({ createdAt: -1 })
    console.log('  ✓ Created index on createdAt (descending)')

    // Text search index for quotes
    try {
      await quotes.createIndex({
        cliente: 'text',
        consulta: 'text',
        direccion: 'text',
      })
      console.log('  ✓ Created text search index')
    } catch (err) {
      console.log('  ⚠ Text search index may already exist or failed')
    }

    // Context indexes
    console.log('\nCreating indexes for context collection...')
    const context = db.collection('context')
    await context.createIndex(
      { session_id: 1, user_phone: 1 },
      { unique: true }
    )
    console.log('  ✓ Created unique compound index on session_id + user_phone')
    await context.createIndex({ last_updated: -1 })
    console.log('  ✓ Created index on last_updated (descending)')

    // Sessions indexes
    console.log('\nCreating indexes for sessions collection...')
    const sessions = db.collection('sessions')
    await sessions.createIndex({ session_id: 1 }, { unique: true })
    console.log('  ✓ Created unique index on session_id')
    await sessions.createIndex({ user_phone: 1 })
    console.log('  ✓ Created index on user_phone')
    await sessions.createIndex({ last_activity: -1 })
    console.log('  ✓ Created index on last_activity (descending)')

    // Settings indexes
    console.log('\nCreating indexes for settings collection...')
    const settings = db.collection('settings')
    await settings.createIndex({ scope: 1, userId: 1 })
    console.log('  ✓ Created compound index on scope + userId')
    await settings.createIndex({ updatedAt: -1 })
    console.log('  ✓ Created index on updatedAt (descending)')

    // Notifications indexes
    console.log('\nCreating indexes for notifications collection...')
    const notifications = db.collection('notifications')
    await notifications.createIndex({ timestamp: -1 })
    console.log('  ✓ Created index on timestamp (descending)')
    await notifications.createIndex({ read: 1, timestamp: -1 })
    console.log('  ✓ Created compound index on read + timestamp')
    await notifications.createIndex({ userId: 1 })
    console.log('  ✓ Created index on userId')
    await notifications.createIndex({ type: 1 })
    console.log('  ✓ Created index on type')

    // Search history indexes
    console.log('\nCreating indexes for search_history collection...')
    const searchHistory = db.collection('search_history')
    await searchHistory.createIndex({ timestamp: -1 })
    console.log('  ✓ Created index on timestamp (descending)')
    await searchHistory.createIndex({ query: 1 })
    console.log('  ✓ Created index on query')

    console.log('\n✅ All indexes created successfully!')
  } catch (error) {
    console.error('❌ Error creating indexes:', error.message)
    if (error.message.includes('already exists')) {
      console.log('\nNote: Some indexes may already exist. This is normal.')
    } else {
      process.exit(1)
    }
  } finally {
    if (client) {
      await client.close()
      console.log('\nConnection closed.')
    }
  }
}

// Run if executed directly
if (require.main === module) {
  createIndexes().catch((error) => {
    console.error('Fatal error:', error)
    process.exit(1)
  })
}

module.exports = { createIndexes }


