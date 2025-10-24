import { NextRequest, NextResponse } from 'next/server'
import { OpenAI } from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Simulación de base de datos en memoria (en producción usar SQLite/PostgreSQL)
const sessions = new Map<string, any>()
const messageHistory = new Map<string, any[]>()

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, user_phone, message, session_id, message_type, intent } = body

    switch (action) {
      case 'create_session':
        return await createSession(user_phone, message)
      
      case 'add_message':
        return await addMessage(session_id, user_phone, message, message_type, intent)
      
      case 'get_context':
        return await getContext(session_id, user_phone)
      
      case 'compress_context':
        return await compressContext(session_id)
      
      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
    }
  } catch (error) {
    console.error('Context API Error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

async function createSession(user_phone: string, initial_message: string) {
  const session_id = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  
  const session = {
    session_id,
    user_phone,
    current_intent: 'greeting',
    context_summary: '',
    token_count: 0,
    created_at: new Date().toISOString(),
    last_activity: new Date().toISOString(),
    status: 'active'
  }
  
  sessions.set(session_id, session)
  messageHistory.set(session_id, [])
  
  if (initial_message) {
    await addMessage(session_id, user_phone, initial_message, 'user', 'new_conversation')
  }
  
  return NextResponse.json({
    action: 'session_created',
    session_id,
    status: 'success'
  })
}

async function addMessage(session_id: string, user_phone: string, message: string, message_type: string, intent?: string) {
  const session = sessions.get(session_id)
  if (!session) {
    return NextResponse.json({ error: 'Session not found' }, { status: 404 })
  }
  
  // Estimar tokens (aproximación simple)
  const token_count = Math.ceil(message.length / 4)
  
  const messageData = {
    message_type,
    content: message,
    intent: intent || session.current_intent,
    token_count,
    timestamp: new Date().toISOString()
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
  if (session.token_count > 6000) { // 80% de 8000
    await compressContext(session_id)
  }
  
  sessions.set(session_id, session)
  
  return NextResponse.json({
    action: 'message_added',
    session_id,
    success: true,
    token_count: session.token_count
  })
}

async function getContext(session_id: string, user_phone: string) {
  const session = sessions.get(session_id)
  if (!session) {
    return NextResponse.json({ error: 'Session not found' }, { status: 404 })
  }
  
  const history = messageHistory.get(session_id) || []
  
  return NextResponse.json({
    session_id,
    user_phone,
    current_intent: session.current_intent,
    conversation_history: history,
    context_summary: session.context_summary,
    token_count: session.token_count,
    status: session.status,
    created_at: session.created_at,
    last_activity: session.last_activity
  })
}

async function compressContext(session_id: string) {
  const session = sessions.get(session_id)
  if (!session) {
    return NextResponse.json({ error: 'Session not found' }, { status: 404 })
  }
  
  const history = messageHistory.get(session_id) || []
  
  // Generar resumen usando OpenAI
  try {
    const recentMessages = history.slice(-5) // Últimos 5 mensajes
    const contextText = recentMessages.map(msg => 
      `${msg.message_type}: ${msg.content}`
    ).join('\n')
    
    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'Genera un resumen conciso del contexto de esta conversación, manteniendo solo la información esencial para continuar la conversación.'
        },
        {
          role: 'user',
          content: `Resume este contexto de conversación:\n\n${contextText}`
        }
      ],
      max_tokens: 200,
      temperature: 0.3
    })
    
    const summary = completion.choices[0]?.message?.content || 'Contexto comprimido'
    
    // Actualizar sesión con resumen
    session.context_summary = summary
    session.token_count = Math.ceil(summary.length / 4) + 100 // Resumen + overhead
    session.last_activity = new Date().toISOString()
    
    // Mantener solo mensajes recientes
    messageHistory.set(session_id, recentMessages)
    
    sessions.set(session_id, session)
    
    return NextResponse.json({
      action: 'context_compressed',
      session_id,
      summary,
      new_token_count: session.token_count,
      success: true
    })
    
  } catch (error) {
    console.error('Error compressing context:', error)
    return NextResponse.json({ error: 'Failed to compress context' }, { status: 500 })
  }
}

// Endpoint para obtener todas las sesiones (para el dashboard)
export async function GET() {
  const allSessions = Array.from(sessions.values()).map(session => ({
    ...session,
    message_count: messageHistory.get(session.session_id)?.length || 0
  }))
  
  return NextResponse.json({
    sessions: allSessions,
    total: allSessions.length,
    active: allSessions.filter(s => s.status === 'active').length
  })
}
