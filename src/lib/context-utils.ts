/**
 * Context Utilities
 * Helper functions for context formatting, manipulation, and validation
 */

import { ConversationContext, Message } from './shared-context-service'

/**
 * Format context for different AI models
 */
export function formatContextForModel(
  context: ConversationContext,
  modelType: 'openai' | 'anthropic' | 'generic' = 'openai'
): any[] {
  const messages: any[] = []

  for (const msg of context.messages) {
    if (modelType === 'openai' || modelType === 'generic') {
      messages.push({
        role: msg.role,
        content: msg.content,
      })
    } else if (modelType === 'anthropic') {
      // Anthropic uses 'user' and 'assistant' roles
      messages.push({
        role: msg.role === 'system' ? 'user' : msg.role,
        content: msg.content,
      })
    }
  }

  return messages
}

/**
 * Extract key information from context
 */
export function extractKeyInfo(context: ConversationContext): {
  intent?: string
  entities?: Record<string, any>
  quoteState?: {
    estado: string
    datos_cliente: Record<string, any>
    datos_producto: Record<string, any>
  }
  lastMessage?: string
  messageCount: number
} {
  return {
    intent: context.intent,
    entities: context.entities,
    quoteState: context.quote_state,
    lastMessage:
      context.messages.length > 0
        ? context.messages[context.messages.length - 1].content
        : undefined,
    messageCount: context.messages.length,
  }
}

/**
 * Merge contexts from multiple sources
 */
export function mergeContexts(
  contexts: ConversationContext[]
): ConversationContext | null {
  if (contexts.length === 0) {
    return null
  }

  if (contexts.length === 1) {
    return contexts[0]
  }

  // Use the first context as base
  const base = { ...contexts[0] }

  // Merge messages (chronologically)
  const allMessages: Message[] = []
  for (const ctx of contexts) {
    allMessages.push(...ctx.messages)
  }

  // Sort by timestamp
  allMessages.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())

  // Merge entities (later contexts override earlier ones)
  const mergedEntities: Record<string, any> = {}
  for (const ctx of contexts) {
    if (ctx.entities) {
      Object.assign(mergedEntities, ctx.entities)
    }
  }

  // Use the most recent intent
  const latestIntent = contexts[contexts.length - 1].intent || base.intent

  // Use the most recent quote state
  const latestQuoteState =
    contexts[contexts.length - 1].quote_state || base.quote_state

  return {
    ...base,
    messages: allMessages,
    entities: mergedEntities,
    intent: latestIntent,
    quote_state: latestQuoteState,
    last_updated: new Date(),
  }
}

/**
 * Validate context structure
 */
export function validateContext(context: any): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []

  if (!context.session_id) {
    errors.push('Missing session_id')
  }

  if (!context.user_phone) {
    errors.push('Missing user_phone')
  }

  if (!context.messages) {
    errors.push('Missing messages array')
  } else if (!Array.isArray(context.messages)) {
    errors.push('messages must be an array')
  } else {
    // Validate each message
    for (let i = 0; i < context.messages.length; i++) {
      const msg = context.messages[i]
      if (!msg.role) {
        errors.push(`Message ${i} missing role`)
      }
      if (!['user', 'assistant', 'system'].includes(msg.role)) {
        errors.push(`Message ${i} has invalid role: ${msg.role}`)
      }
      if (!msg.content) {
        errors.push(`Message ${i} missing content`)
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * Compress context by summarizing old messages
 */
export function compressContext(
  context: ConversationContext,
  keepRecent: number = 10
): ConversationContext {
  if (context.messages.length <= keepRecent) {
    return context
  }

  // Keep recent messages
  const recentMessages = context.messages.slice(-keepRecent)

  // Create summary of older messages
  const oldMessages = context.messages.slice(0, -keepRecent)
  const summaryMessage: Message = {
    role: 'system',
    content: `Previous conversation summary: ${
      oldMessages.length
    } messages about ${context.intent || 'general topics'}`,
    timestamp: new Date(),
  }

  return {
    ...context,
    messages: [summaryMessage, ...recentMessages],
    context_summary: `Compressed from ${context.messages.length} to ${
      keepRecent + 1
    } messages`,
    last_updated: new Date(),
  }
}

/**
 * Extract conversation summary
 */
export function getConversationSummary(context: ConversationContext): string {
  if (context.context_summary) {
    return context.context_summary
  }

  const keyInfo = extractKeyInfo(context)
  const parts: string[] = []

  if (keyInfo.intent) {
    parts.push(`Intent: ${keyInfo.intent}`)
  }

  if (keyInfo.quoteState) {
    parts.push(`Quote state: ${keyInfo.quoteState.estado}`)
  }

  parts.push(`${keyInfo.messageCount} messages exchanged`)

  return parts.join('. ')
}
