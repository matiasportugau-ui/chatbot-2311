/**
 * Shared Context Service
 * Provides a unified interface for managing conversation context across agents
 * Supports both MongoDB persistence and in-memory fallback
 */

import { connectDB } from './mongodb'

interface ContextMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: Record<string, any>
}

interface ConversationContext {
  session_id: string
  user_phone: string
  messages: ContextMessage[]
  context_summary?: string
  intent?: string
  token_count: number
  last_updated: Date
  metadata?: Record<string, any>
}

interface SessionMetadata {
  session_id: string
  user_phone: string
  created_at: Date
  last_activity: Date
  status: 'active' | 'closed' | 'expired'
  agent_type?: string
  source?: string
  metadata?: Record<string, any>
}

class SharedContextService {
  private inMemoryContexts: Map<string, ConversationContext> = new Map()
  private inMemorySessions: Map<string, SessionMetadata> = new Map()
  private useMongoDb: boolean = true

  constructor() {
    // Try to use MongoDB by default, fallback to in-memory
    this.useMongoDb = !!process.env.MONGODB_URI
  }

  /**
   * Create a new session
   */
  async createSession(
    userPhone: string,
    initialMessage?: string,
    metadata?: Record<string, any>
  ): Promise<string> {
    const sessionId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const now = new Date()

    const session: SessionMetadata = {
      session_id: sessionId,
      user_phone: userPhone,
      created_at: now,
      last_activity: now,
      status: 'active',
      agent_type: metadata?.agent_type,
      source: metadata?.source,
      metadata,
    }

    const context: ConversationContext = {
      session_id: sessionId,
      user_phone: userPhone,
      messages: [],
      token_count: 0,
      last_updated: now,
      metadata,
    }

    // Add initial message if provided
    if (initialMessage) {
      context.messages.push({
        role: 'user',
        content: initialMessage,
        timestamp: now,
      })
      context.token_count = Math.ceil(initialMessage.length / 4)
    }

    // Try to persist to MongoDB
    if (this.useMongoDb) {
      try {
        const db = await connectDB()
        await db.collection('sessions').insertOne(session)
        await db.collection('contexts').insertOne(context)
      } catch (error) {
        console.warn('MongoDB not available, using in-memory storage:', error)
        this.useMongoDb = false
      }
    }

    // Always store in-memory as fallback
    this.inMemorySessions.set(sessionId, session)
    this.inMemoryContexts.set(sessionId, context)

    return sessionId
  }

  /**
   * Get session metadata
   */
  async getSession(sessionId: string): Promise<SessionMetadata | null> {
    // Try MongoDB first
    if (this.useMongoDb) {
      try {
        const db = await connectDB()
        const session = await db.collection('sessions').findOne({ session_id: sessionId })
        if (session) {
          return session as unknown as SessionMetadata
        }
      } catch (error) {
        console.warn('MongoDB error, falling back to in-memory:', error)
      }
    }

    // Fallback to in-memory
    return this.inMemorySessions.get(sessionId) || null
  }

  /**
   * Get conversation context
   */
  async getContext(
    sessionId: string,
    userPhone: string
  ): Promise<ConversationContext | null> {
    // Try MongoDB first
    if (this.useMongoDb) {
      try {
        const db = await connectDB()
        const context = await db.collection('contexts').findOne({
          session_id: sessionId,
          user_phone: userPhone,
        })
        if (context) {
          return context as unknown as ConversationContext
        }
      } catch (error) {
        console.warn('MongoDB error, falling back to in-memory:', error)
      }
    }

    // Fallback to in-memory
    const context = this.inMemoryContexts.get(sessionId)
    if (context && context.user_phone === userPhone) {
      return context
    }
    return null
  }

  /**
   * Save/update conversation context
   */
  async saveContext(
    sessionId: string,
    context: Partial<ConversationContext>
  ): Promise<boolean> {
    const now = new Date()
    const updatedContext = {
      ...context,
      session_id: sessionId,
      last_updated: now,
    }

    // Try MongoDB first
    if (this.useMongoDb) {
      try {
        const db = await connectDB()
        await db.collection('contexts').updateOne(
          { session_id: sessionId },
          { $set: updatedContext },
          { upsert: true }
        )
        // Also update session last_activity
        await db.collection('sessions').updateOne(
          { session_id: sessionId },
          { $set: { last_activity: now } }
        )
      } catch (error) {
        console.warn('MongoDB error, using in-memory:', error)
      }
    }

    // Always update in-memory
    const existingContext = this.inMemoryContexts.get(sessionId)
    if (existingContext) {
      this.inMemoryContexts.set(sessionId, {
        ...existingContext,
        ...updatedContext,
      } as ConversationContext)
    } else {
      this.inMemoryContexts.set(sessionId, updatedContext as ConversationContext)
    }

    // Update session last_activity
    const existingSession = this.inMemorySessions.get(sessionId)
    if (existingSession) {
      existingSession.last_activity = now
    }

    return true
  }

  /**
   * Add a message to conversation context
   */
  async addMessage(
    sessionId: string,
    content: string,
    role: 'user' | 'assistant' | 'system',
    metadata?: Record<string, any>
  ): Promise<boolean> {
    const now = new Date()
    const message: ContextMessage = {
      role,
      content,
      timestamp: now,
      metadata,
    }

    const tokenCount = Math.ceil(content.length / 4)

    // Try MongoDB first
    if (this.useMongoDb) {
      try {
        const db = await connectDB()
        await db.collection('contexts').updateOne(
          { session_id: sessionId },
          {
            $push: { messages: message } as any,
            $inc: { token_count: tokenCount },
            $set: { last_updated: now },
          }
        )
        // Update session last_activity
        await db.collection('sessions').updateOne(
          { session_id: sessionId },
          { $set: { last_activity: now } }
        )
      } catch (error) {
        console.warn('MongoDB error, using in-memory:', error)
      }
    }

    // Always update in-memory
    const context = this.inMemoryContexts.get(sessionId)
    if (context) {
      context.messages.push(message)
      context.token_count += tokenCount
      context.last_updated = now
    }

    // Update session last_activity
    const session = this.inMemorySessions.get(sessionId)
    if (session) {
      session.last_activity = now
    }

    return true
  }

  /**
   * List sessions for a user or all sessions
   */
  async listSessions(
    userPhone?: string,
    limit: number = 50
  ): Promise<SessionMetadata[]> {
    // Try MongoDB first
    if (this.useMongoDb) {
      try {
        const db = await connectDB()
        const query = userPhone ? { user_phone: userPhone } : {}
        const sessions = await db
          .collection('sessions')
          .find(query)
          .sort({ last_activity: -1 })
          .limit(limit)
          .toArray()
        return sessions as unknown as SessionMetadata[]
      } catch (error) {
        console.warn('MongoDB error, falling back to in-memory:', error)
      }
    }

    // Fallback to in-memory
    let sessions = Array.from(this.inMemorySessions.values())
    if (userPhone) {
      sessions = sessions.filter((s) => s.user_phone === userPhone)
    }
    return sessions
      .sort((a, b) => b.last_activity.getTime() - a.last_activity.getTime())
      .slice(0, limit)
  }

  /**
   * Close a session
   */
  async closeSession(sessionId: string): Promise<boolean> {
    const now = new Date()

    // Try MongoDB first
    if (this.useMongoDb) {
      try {
        const db = await connectDB()
        await db.collection('sessions').updateOne(
          { session_id: sessionId },
          { $set: { status: 'closed', last_activity: now } }
        )
      } catch (error) {
        console.warn('MongoDB error:', error)
      }
    }

    // Update in-memory
    const session = this.inMemorySessions.get(sessionId)
    if (session) {
      session.status = 'closed'
      session.last_activity = now
    }

    return true
  }
}

// Singleton instance
let sharedContextService: SharedContextService | null = null

/**
 * Get the shared context service instance
 */
export function getSharedContextService(): SharedContextService {
  if (!sharedContextService) {
    sharedContextService = new SharedContextService()
  }
  return sharedContextService
}

export type { ConversationContext, SessionMetadata, ContextMessage }
