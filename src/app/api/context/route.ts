export const dynamic = 'force-dynamic'

import { getSharedContextService } from '@/lib/shared-context-service'

import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'

import { OpenAI } from 'openai'
import {
  successResponse,
  errorResponse,
  validationErrorResponse,
  notFoundResponse,
} from '@/lib/api-response'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Use shared context service (with in-memory fallback)
const sharedService = getSharedContextService()

// Fallback in-memory storage (for backward compatibility)
const sessions = new Map<string, any>()
const messageHistory = new Map<string, any[]>()

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, user_phone, message, session_id, message_type, intent } =
      body

    switch (action) {
      case 'create_session':
        return await createSession(user_phone, message)

      case 'add_message':
        return await addMessage(
          session_id,
          user_phone,
          message,
          message_type,
          intent
        )

      case 'get_context':
        return await getContext(session_id, user_phone)

      case 'compress_context':
        return await compressContext(session_id)

      default:
        return validationErrorResponse(
          ['Invalid action'],
          'Invalid action parameter'
        )
    }
  } catch (error: unknown) {
    console.error('Context API Error:', error)
    const errorMessage = error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}

async function createSession(user_phone: string, initial_message: string) {
  try {
    // Use shared service to create session
    const session_id = await sharedService.createSession(
      user_phone,
      initial_message,
      {
        source: 'context_api',
        agent_type: 'nextjs',
      }
    )

    // Also maintain in-memory for backward compatibility
    const session = {
      session_id,
      user_phone,
      current_intent: 'greeting',
      context_summary: '',
      token_count: 0,
      created_at: new Date().toISOString(),
      last_activity: new Date().toISOString(),
      status: 'active',
    }

    sessions.set(session_id, session)
    messageHistory.set(session_id, [])

    if (initial_message) {
      await addMessage(
        session_id,
        user_phone,
        initial_message,
        'user',
        'new_conversation'
      )
    }

    return successResponse({
      action: 'session_created',
      session_id,
      status: 'success',
    })
  } catch (error: unknown) {
    console.error('Error creating session:', error)
    // Fallback to in-memory only
    const session_id = `sess_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`
    const session = {
      session_id,
      user_phone,
      current_intent: 'greeting',
      context_summary: '',
      token_count: 0,
      created_at: new Date().toISOString(),
      last_activity: new Date().toISOString(),
      status: 'active',
    }
    sessions.set(session_id, session)
    messageHistory.set(session_id, [])
    return successResponse({
      action: 'session_created',
      session_id,
      status: 'success',
    })
  }
}

async function addMessage(
  session_id: string,
  user_phone: string,
  message: string,
  message_type: string,
  intent?: string
) {
  const session = sessions.get(session_id)
  if (!session) {
    return notFoundResponse('Session')
  }

  // Map message_type to role for shared service
  const role =
    message_type === 'user'
      ? 'user'
      : message_type === 'assistant'
        ? 'assistant'
        : 'system'

  // Add message to shared service
  try {
    await sharedService.addMessage(session_id, message, role, {
      intent,
      message_type,
    })
  } catch (error) {
    console.warn('Failed to add message to shared service:', error)
  }

  // Estimar tokens (aproximación simple)
  const token_count = Math.ceil(message.length / 4)

  const messageData = {
    message_type,
    content: message,
    intent: intent || session.current_intent,
    token_count,
    timestamp: new Date().toISOString(),
  }

  // Agregar mensaje al historial
  const history = messageHistory.get(session_id) || []
  history.push(messageData)
  messageHistory.set(session_id, history)

  // Actualizar sesión
  session.token_count += token_count
  session.last_activity = new Date().toISOString()
  if (intent) {
    session.current_intent = intent
  }

  // Verificar si necesita compresión
  if (session.token_count > 6000) {
    // 80% de 8000
    await compressContext(session_id)
  }

  sessions.set(session_id, session)

  return successResponse({
    action: 'message_added',
    session_id,
    success: true,
    token_count: session.token_count,
  })
}

async function getContext(session_id: string, user_phone: string) {
  // Try to get from shared service first
  try {
    const sharedContext = await sharedService.getContext(session_id, user_phone)
    if (sharedContext) {
      // Convert shared context format to legacy format
      return successResponse({
        session_id,
        user_phone,
        current_intent: sharedContext.intent || 'general',
        conversation_history: sharedContext.messages || [],
        context_summary: sharedContext.context_summary || '',
        token_count: sharedContext.token_count || 0,
        status: 'active',
        created_at: sharedContext.last_updated.toISOString(),
        last_activity: sharedContext.last_updated.toISOString(),
      })
    }
  } catch (error: unknown) {
    console.warn('Failed to get context from shared service:', error)
  }

  // Fallback to in-memory
  const session = sessions.get(session_id)
  if (!session) {
    return notFoundResponse('Session')
  }

  const history = messageHistory.get(session_id) || []

  return successResponse({
    session_id,
    user_phone,
    current_intent: session.current_intent,
    conversation_history: history,
    context_summary: session.context_summary,
    token_count: session.token_count,
    status: session.status,
    created_at: session.created_at,
    last_activity: session.last_activity,
  })
}

async function compressContext(session_id: string) {
  const session = sessions.get(session_id)
  if (!session) {
    return notFoundResponse('Session')
  }

  const history = messageHistory.get(session_id) || []

  // Generar resumen usando OpenAI
  try {
    const recentMessages = history.slice(-5) // Últimos 5 mensajes
    const contextText = recentMessages
      .map(msg => `${msg.message_type}: ${msg.content}`)
      .join('\n')

    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content:
            'Genera un resumen conciso del contexto de esta conversación, manteniendo solo la información esencial para continuar la conversación.',
        },
        {
          role: 'user',
          content: `Resume este contexto de conversación:\n\n${contextText}`,
        },
      ],
      max_tokens: 200,
      temperature: 0.3,
    })

    const summary =
      completion.choices[0]?.message?.content || 'Contexto comprimido'

    // Actualizar sesión con resumen
    session.context_summary = summary
    session.token_count = Math.ceil(summary.length / 4) + 100 // Resumen + overhead
    session.last_activity = new Date().toISOString()

    // Mantener solo mensajes recientes
    messageHistory.set(session_id, recentMessages)

    sessions.set(session_id, session)

    return successResponse({
      action: 'context_compressed',
      session_id,
      summary,
      new_token_count: session.token_count,
      success: true,
    })
  } catch (error: unknown) {
    console.error('Error compressing context:', error)
    const errorMessage = error instanceof Error ? error.message : 'Internal server error'
    return errorResponse('Failed to compress context', 500, errorMessage)
  }
}

// Endpoint para obtener todas las sesiones (para el dashboard)
export async function GET() {
  const allSessions = Array.from(sessions.values()).map(session => ({
    ...session,
    message_count: messageHistory.get(session.session_id)?.length || 0,
  }))

  return successResponse({
    sessions: allSessions,
    total: allSessions.length,
    active: allSessions.filter(s => s.status === 'active').length,
  })
}
