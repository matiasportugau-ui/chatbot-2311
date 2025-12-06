/**
 * Shared Context Service for Multi-Agent System
 * Provides unified MongoDB-based context management for all agents
 */

import { connectDB } from './mongodb'

export interface SessionMetadata {
  session_id: string
  user_phone: string
  created_at: Date
  last_activity: Date
  status: 'active' | 'expired' | 'archived'
  metadata?: {
    agent_type?: string
    source?: string
    tags?: string[]
  }
}

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: any
}

export interface ConversationContext {
  session_id: string
  user_phone: string
  messages: Message[]
  intent?: string
  entities?: Record<string, any>
  quote_state?: {
    estado: string
    datos_cliente: Record<string, any>
    datos_producto: Record<string, any>
  }
  token_count?: number
  context_summary?: string
  last_updated: Date
}

class SharedContextService {
  private inMemorySessions: Map<string, SessionMetadata> = new Map()
  private inMemoryContexts: Map<string, ConversationContext> = new Map()

  /**
   * Retrieve full conversation context for a session
   */
  async getContext(
    sessionId: string,
    userPhone: string
  ): Promise<ConversationContext | null> {
    try {
      const db = await connectDB()
      const context = db.collection<ConversationContext>('context')

      const contextDoc = await context.findOne({
        session_id: sessionId,
        user_phone: userPhone,
      })

      if (contextDoc) {
        return contextDoc
      }

      // Fallback to in-memory
      const key = `${userPhone}_${sessionId}`
      return this.inMemoryContexts.get(key) || null
    } catch (error) {
      console.warn('Error getting context from MongoDB:', error)
      // Fallback to in-memory
      const key = `${userPhone}_${sessionId}`
      return this.inMemoryContexts.get(key) || null
    }
  }

  /**
   * Save/update conversation context
   */
  async saveContext(
    sessionId: string,
    context: ConversationContext
  ): Promise<boolean> {
    try {
      const db = await connectDB()
      const contextCol = db.collection<ConversationContext>('context')

      const contextDoc = {
        ...context,
        session_id: sessionId,
        user_phone: context.user_phone,
        last_updated: new Date(),
      }

      await contextCol.updateOne(
        { session_id: sessionId, user_phone: context.user_phone },
        { $set: contextDoc },
        { upsert: true }
      )

      // Update in-memory cache
      const key = `${context.user_phone}_${sessionId}`
      this.inMemoryContexts.set(key, contextDoc as ConversationContext)

      return true
    } catch (error) {
      console.error('Error saving context to MongoDB:', error)
      // Fallback to in-memory
      const key = `${context.user_phone}_${sessionId}`
      this.inMemoryContexts.set(key, context)
      return false
    }
  }

  /**
   * Add message to conversation history
   */
  async addMessage(
    sessionId: string,
    message: string,
    role: 'user' | 'assistant' | 'system',
    metadata?: any
  ): Promise<boolean> {
    try {
      const db = await connectDB()
      const contextCol = db.collection<ConversationContext>('context')

      const messageEntry: Message = {
        role,
        content: message,
        timestamp: new Date(),
        metadata: metadata || {},
      }

      await contextCol.updateOne(
        { session_id: sessionId },
        {
          $push: { messages: messageEntry },
          $set: { last_updated: new Date() },
        }
      )

      // Update in-memory cache
      const key = Array.from(this.inMemoryContexts.keys()).find(k =>
        k.endsWith(`_${sessionId}`)
      )
      if (key) {
        const context = this.inMemoryContexts.get(key)
        if (context) {
          context.messages.push(messageEntry)
          context.last_updated = new Date()
        }
      }

      return true
    } catch (error) {
      console.error('Error adding message:', error)
      return false
    }
  }

  /**
   * Get session metadata
   */
  async getSession(sessionId: string): Promise<SessionMetadata | null> {
    try {
      const db = await connectDB()
      const sessions = db.collection<SessionMetadata>('sessions')

      const sessionDoc = await sessions.findOne({ session_id: sessionId })

      if (sessionDoc) {
        return sessionDoc
      }

      // Fallback to in-memory
      return this.inMemorySessions.get(sessionId) || null
    } catch (error) {
      console.warn('Error getting session from MongoDB:', error)
      return this.inMemorySessions.get(sessionId) || null
    }
  }

  /**
   * Create new session
   */
  async createSession(
    userPhone: string,
    initialMessage?: string,
    metadata?: {
      agent_type?: string
      source?: string
      tags?: string[]
    }
  ): Promise<string> {
    const sessionId = `sess_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`

    const sessionData: SessionMetadata = {
      session_id: sessionId,
      user_phone: userPhone,
      created_at: new Date(),
      last_activity: new Date(),
      status: 'active',
      metadata: metadata || {},
    }

    try {
      const db = await connectDB()
      const sessions = db.collection<SessionMetadata>('sessions')

      await sessions.insertOne(sessionData)

      // Create initial context if message provided
      if (initialMessage) {
        await this.addMessage(sessionId, initialMessage, 'user')
      }

      // Update in-memory cache
      this.inMemorySessions.set(sessionId, sessionData)

      return sessionId
    } catch (error) {
      console.warn('Error creating session in MongoDB:', error)
      // Fallback to in-memory
      this.inMemorySessions.set(sessionId, sessionData)
      if (initialMessage) {
        await this.addMessage(sessionId, initialMessage, 'user')
      }
      return sessionId
    }
  }

  /**
   * List sessions for a user or all sessions
   */
  async listSessions(
    userPhone?: string,
    limit: number = 50
  ): Promise<SessionMetadata[]> {
    try {
      const db = await connectDB()
      const sessions = db.collection<SessionMetadata>('sessions')

      const query = userPhone ? { user_phone: userPhone } : {}

      const sessionDocs = await sessions
        .find(query)
        .sort({ last_activity: -1 })
        .limit(limit)
        .toArray()

      return sessionDocs
    } catch (error) {
      console.warn('Error listing sessions from MongoDB:', error)
      // Fallback to in-memory
      const result: SessionMetadata[] = []
      const sessionsArray = Array.from(this.inMemorySessions.values())
      for (const session of sessionsArray) {
        if (!userPhone || session.user_phone === userPhone) {
          result.push(session)
        }
      }
      result.sort(
        (a, b) => b.last_activity.getTime() - a.last_activity.getTime()
      )
      return result.slice(0, limit)
    }
  }
}

// Singleton instance
let sharedContextService: SharedContextService | null = null

export function getSharedContextService(): SharedContextService {
  if (!sharedContextService) {
    sharedContextService = new SharedContextService()
  }
  return sharedContextService
}
