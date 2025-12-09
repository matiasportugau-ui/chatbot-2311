'use client'

import React, { useEffect, useRef, useState, useCallback } from 'react'
// @ts-ignore - AI SDK v5 exports useChat from main package
import { useChat } from 'ai/react'
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
  Zap,
  Calculator,
  Building2,
  Info
} from 'lucide-react'

interface ChatInterfaceEvolvedProps {
  userPhone?: string
  className?: string
  sessionId?: string
}

export function ChatInterfaceEvolved({
  userPhone = '+59891234567',
  className,
  sessionId: initialSessionId
}: ChatInterfaceEvolvedProps) {
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null)
  const [contextUsage, setContextUsage] = useState(0)
  const [quoteMetadata, setQuoteMetadata] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Use refs to track latest values for reliable request data
  // This fixes Bug 1 & 2: body parameter doesn't update and may not be sent reliably
  const sessionIdRef = useRef<string | null>(initialSessionId || null)
  const userPhoneRef = useRef<string>(userPhone)

  // Update refs when state changes
  useEffect(() => {
    sessionIdRef.current = sessionId
  }, [sessionId])

  useEffect(() => {
    userPhoneRef.current = userPhone
  }, [userPhone])

  // Use AI SDK's useChat hook
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit: originalHandleSubmit,
    isLoading,
    error,
    setMessages,
    reload
  } = useChat({
    api: '/api/chat/stream',
    // Note: body parameter may not be reliably sent in AI SDK v5.0.78
    // We use a custom fetch function to ensure data is always sent correctly
    fetch: async (input, init) => {
      // Parse existing body if present
      let requestBody: any = {}
      if (init?.body) {
        try {
          requestBody = typeof init.body === 'string'
            ? JSON.parse(init.body)
            : init.body
        } catch (e) {
          // If parsing fails, use empty object
          requestBody = {}
        }
      }

      // Always inject latest sessionId and userPhone into data property
      // This ensures Bug 1 & 2 are fixed: data is always current and reliably sent
      requestBody.data = {
        userPhone: userPhoneRef.current,
        sessionId: sessionIdRef.current || undefined,
      }

      // Create new request with updated body
      return fetch(input, {
        ...init,
        headers: {
          ...init?.headers,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })
    },
    onResponse: (response: Response) => {
      // Extract metadata from headers
      const quoteType = response.headers.get('X-Quote-Type')
      const confidence = response.headers.get('X-Confidence')
      const sessionIdHeader = response.headers.get('X-Session-Id')

      if (sessionIdHeader) {
        setSessionId(sessionIdHeader)
        sessionIdRef.current = sessionIdHeader
      }

      if (quoteType) {
        // Safely parse confidence header, defaulting to 0 if missing or invalid
        // The API only sends X-Confidence header when parsedData.confianza is a valid number
        let confianzaValue = 0
        if (confidence) {
          const parsed = parseFloat(confidence)
          // Double-check: ensure parsed value is a valid finite number
          if (!isNaN(parsed) && isFinite(parsed) && parsed >= 0 && parsed <= 1) {
            confianzaValue = parsed
          }
        }

        setQuoteMetadata({
          tipo: quoteType,
          confianza: confianzaValue,
        })
      }
    },
    onError: (error: Error) => {
      console.error('Chat error:', error)
    },
    onFinish: (message: any) => {
      // Update context usage after message
      updateContextUsage()
    },
  })

  // Initialize session function (after useChat to access messages and setMessages)
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
        setSessionId(data.session_id)
        sessionIdRef.current = data.session_id

        // Add welcome message if no messages exist
        if (messages.length === 0) {
          setMessages([{
            id: 'welcome',
            role: 'assistant',
            content: '¡Hola! Soy tu asistente de cotizaciones de BMC Construcciones. ¿En qué puedo ayudarte hoy?'
          }])
        }
      }
    } catch (error) {
      console.error('Error initializing session:', error)
    }
  }, [userPhone, messages, setMessages])

  // Initialize session on mount
  useEffect(() => {
    if (!sessionId && messages.length === 0) {
      initializeSession()
    }
  }, [sessionId, messages.length, initializeSession])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Update context usage
  const updateContextUsage = async () => {
    if (!sessionId) return

    try {
      const response = await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'get_context',
          session_id: sessionId,
          user_phone: userPhone
        })
      })

      const data = await response.json()
      if (data.token_count) {
        setContextUsage((data.token_count / 8000) * 100)
      }
    } catch (error) {
      console.error('Error updating context:', error)
    }
  }

  // Compress context
  const compressContext = async () => {
    if (!sessionId) return

    try {
      const response = await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'compress_context',
          session_id: sessionId
        })
      })

      const data = await response.json()
      if (data.success) {
        await updateContextUsage()
      }
    } catch (error) {
      console.error('Error compressing context:', error)
    }
  }

  // Create new chat
  const createNewChat = async () => {
    await initializeSession()
    setMessages([])
    setContextUsage(0)
    setQuoteMetadata(null)
  }

  // Get message icon
  const getMessageIcon = (role: string) => {
    switch (role) {
      case 'user': return <User className="w-4 h-4" />
      case 'assistant': return <Bot className="w-4 h-4" />
      case 'system': return <MessageSquare className="w-4 h-4" />
      default: return <MessageSquare className="w-4 h-4" />
    }
  }

  // Get message color
  const getMessageColor = (role: string) => {
    switch (role) {
      case 'user': return 'bg-blue-100 text-blue-800'
      case 'assistant': return 'bg-green-100 text-green-800'
      case 'system': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Custom submit handler to add metadata and ensure latest session data
  const handleCustomSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Save message to context API using latest sessionId from ref
    const currentSessionId = sessionIdRef.current
    if (currentSessionId && input.trim()) {
      try {
        await fetch('/api/context', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'add_message',
            session_id: currentSessionId,
            user_phone: userPhoneRef.current,
            message: input,
            message_type: 'user',
            intent: 'user_input'
          })
        })
      } catch (error) {
        console.error('Error saving message:', error)
      }
    }

    // Use AI SDK's submit handler (fetch interceptor will add latest data)
    originalHandleSubmit(e)
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Chat de Cotizaciones (Evolved)
            </CardTitle>
            <div className="flex items-center gap-2">
              {sessionId && (
                <Badge variant="outline" className="text-xs">
                  {sessionId.slice(0, 8)}...
                </Badge>
              )}
              {quoteMetadata && (
                <Badge variant="outline" className="text-xs">
                  {quoteMetadata.tipo}
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          {/* Context Usage Bar */}
          {sessionId && (
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
                    disabled={isLoading}
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
                  disabled={isLoading}
                >
                  <RefreshCw className="w-3 h-3 mr-1" />
                  Nuevo Chat
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="mb-4 border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">
                {error.message || 'Error al procesar tu mensaje. Por favor, intenta de nuevo.'}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Messages */}
      <Card className="flex-1 mb-4">
        <CardContent className="p-4 h-96 overflow-y-auto">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                Inicia una conversación para ver el historial.
              </div>
            )}
            {messages.map((message: any) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
              >
                <div className={`p-2 rounded-full ${getMessageColor(message.role)}`}>
                  {getMessageIcon(message.role)}
                </div>
                <div className={`flex-1 max-w-xs ${message.role === 'user' ? 'text-right' : 'text-left'
                  }`}>
                  <div className={`p-3 rounded-lg ${message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : message.role === 'assistant'
                        ? 'bg-gray-100 text-gray-900'
                        : 'bg-yellow-100 text-yellow-900'
                    }`}>
                    <div className="text-sm whitespace-pre-wrap">
                      {message.content}
                    </div>
                    {message.role === 'assistant' && quoteMetadata &&
                      typeof quoteMetadata.confianza === 'number' &&
                      !isNaN(quoteMetadata.confianza) &&
                      isFinite(quoteMetadata.confianza) &&
                      quoteMetadata.confianza > 0 && (
                        <Badge variant="outline" className="text-xs mt-2">
                          Confianza: {(quoteMetadata.confianza * 100).toFixed(1)}%
                        </Badge>
                      )}
                  </div>
                  {message.createdAt && (
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(message.createdAt).toLocaleTimeString()}
                    </p>
                  )}
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
          <form onSubmit={handleCustomSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Escribe tu mensaje..."
              disabled={isLoading || !sessionId}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={isLoading || !input.trim() || !sessionId}
              className="px-4"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

