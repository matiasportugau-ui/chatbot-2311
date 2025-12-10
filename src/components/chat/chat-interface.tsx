'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Send,
  Bot,
  User,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  MessageSquare,
  Zap
} from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  intent?: string
}

interface ChatSession {
  session_id: string
  user_phone: string
  current_intent: string
  token_count: number
  context_summary: string
  status: string
}

interface ChatInterfaceProps {
  userPhone?: string
  className?: string
}

export function ChatInterface({ userPhone = '+59891234567', className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [session, setSession] = useState<ChatSession | null>(null)
  const [contextUsage, setContextUsage] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Inicializar sesión al montar el componente




  const addMessage = (type: 'user' | 'assistant' | 'system', content: string, intent?: string) => {
    const newMessage: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      content,
      timestamp: new Date().toISOString(),
      intent
    }
    setMessages(prev => [...prev, newMessage])
  }

  const initializeSession = useCallback(async () => {
    try {
      const response = await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'create_session',
          user_phone: userPhone,
          message: 'Hola, necesito ayuda con una cotización'
        })
      })

      const data = await response.json()
      if (data.session_id) {
        setSession({
          session_id: data.session_id,
          user_phone: userPhone,
          current_intent: 'greeting',
          token_count: 0,
          context_summary: '',
          status: 'active'
        })

        // Agregar mensaje de bienvenida
        addMessage('assistant', '¡Hola! Soy tu asistente de cotizaciones. ¿En qué puedo ayudarte hoy?', 'greeting')
      }
    } catch (error) {
      console.error('Error initializing session:', error)
    }
  }, [userPhone])

  useEffect(() => {
    initializeSession()
  }, [initializeSession])

  const sendMessage = async () => {
    if (!inputMessage.trim() || !session) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setIsLoading(true)

    // Agregar mensaje del usuario
    addMessage('user', userMessage, 'user_input')

    try {
      // Agregar mensaje a la sesión
      await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add_message',
          session_id: session.session_id,
          user_phone: userPhone,
          message: userMessage,
          message_type: 'user',
          intent: 'user_input'
        })
      })

      // Simular respuesta del asistente (en producción esto vendría de n8n)
      const responses = [
        'Entiendo tu consulta. Déjame ayudarte con eso.',
        'Perfecto, voy a procesar tu solicitud.',
        'Excelente pregunta. Te proporciono la información que necesitas.',
        'Gracias por tu consulta. Aquí tienes la respuesta.',
        'Entendido. Te ayudo con los detalles.'
      ]

      const randomResponse = responses[Math.floor(Math.random() * responses.length)]

      // Simular delay de procesamiento
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

      addMessage('assistant', randomResponse, 'assistant_response')

      // Actualizar contexto
      await updateContext()

    } catch (error) {
      console.error('Error sending message:', error)
      addMessage('system', 'Error al procesar tu mensaje. Por favor, intenta de nuevo.', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const updateContext = async () => {
    if (!session) return

    try {
      const response = await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'get_context',
          session_id: session.session_id,
          user_phone: userPhone
        })
      })

      const data = await response.json()
      if (data.session_id) {
        setSession(prev => prev ? { ...prev, ...data } : null)
        setContextUsage((data.token_count / 8000) * 100)
      }
    } catch (error) {
      console.error('Error updating context:', error)
    }
  }

  const compressContext = async () => {
    if (!session) return

    try {
      const response = await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'compress_context',
          session_id: session.session_id
        })
      })

      const data = await response.json()
      if (data.success) {
        addMessage('system', 'Contexto comprimido para optimizar la conversación.', 'context_compression')
        await updateContext()
      }
    } catch (error) {
      console.error('Error compressing context:', error)
    }
  }

  const createNewChat = async () => {
    try {
      setMessages([])
      setContextUsage(0)
      await initializeSession()
      addMessage('system', 'Nueva conversación iniciada.', 'new_chat')
    } catch (error) {
      console.error('Error creating new chat:', error)
    }
  }

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'user': return <User className="w-4 h-4" />
      case 'assistant': return <Bot className="w-4 h-4" />
      case 'system': return <MessageSquare className="w-4 h-4" />
      default: return <MessageSquare className="w-4 h-4" />
    }
  }

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'user': return 'bg-blue-100 text-blue-800'
      case 'assistant': return 'bg-green-100 text-green-800'
      case 'system': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Chat de Cotizaciones
            </CardTitle>
            <div className="flex items-center gap-2">
              {session && (
                <>
                  <Badge variant="outline" className="text-xs">
                    {session.current_intent}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {session.token_count} tokens
                  </Badge>
                </>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          {/* Context Usage Bar */}
          {session && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Uso de Contexto</span>
                <span className="font-medium">{Math.round(contextUsage)}%</span>
              </div>
              <Progress
                value={contextUsage}
                className="h-2"
              />
              <div className="flex items-center gap-2">
                {contextUsage > 80 && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={compressContext}
                    className="text-xs"
                  >
                    <Zap className="w-3 h-3 mr-1" />
                    Comprimir
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={createNewChat}
                  className="text-xs"
                >
                  <RefreshCw className="w-3 h-3 mr-1" />
                  Nuevo Chat
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Messages */}
      <Card className="flex-1 mb-4">
        <CardContent className="p-4 h-96 overflow-y-auto">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
              >
                <div className={`p-2 rounded-full ${getMessageColor(message.type)}`}>
                  {getMessageIcon(message.type)}
                </div>
                <div className={`flex-1 max-w-xs ${message.type === 'user' ? 'text-right' : 'text-left'
                  }`}>
                  <div className={`p-3 rounded-lg ${message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : message.type === 'assistant'
                      ? 'bg-gray-100 text-gray-900'
                      : 'bg-yellow-100 text-yellow-900'
                    }`}>
                    <p className="text-sm">{message.content}</p>
                    {message.intent && message.intent !== 'user_input' && (
                      <Badge variant="outline" className="text-xs mt-1">
                        {message.intent}
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-full bg-green-100 text-green-800">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="p-3 rounded-lg bg-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
                    <span className="text-sm">Procesando...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </CardContent>
      </Card>

      {/* Input */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Escribe tu mensaje..."
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading || !session}
            />
            <Button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim() || !session}
              className="px-4"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
