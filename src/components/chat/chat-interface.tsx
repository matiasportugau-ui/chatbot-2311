'use client'

import React, { useEffect, useRef, useCallback } from 'react'
import { useChat } from '@ai-sdk/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MessageBubble } from '@/components/chat/message-bubble'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Send,
  Bot,
  User,
  MessageSquare,
  RefreshCw,
  AlertTriangle
} from 'lucide-react'
import '@/styles/character-theme.css'
import Image from 'next/image'

interface ChatInterfaceProps {
  userPhone?: string
  className?: string
}

export function ChatInterface({ userPhone = '+59891234567', className }: ChatInterfaceProps) {
  // Session management using ref to ensure stability across renders
  const sessionIdRef = useRef<string>('')

  // Initialize session ID only once
  if (!sessionIdRef.current) {
    sessionIdRef.current = `session_${userPhone}_${Date.now()}`
  }

  const [metadata, setMetadata] = React.useState<{ confidence?: number; source?: string }>({})
  const inputRef = useRef<HTMLInputElement>(null)

  /* 
     NOTE: Simplified implementation to ensure reliability.
     Using standard useChat fetch and passing body data via append options.
  */
  const { messages, append, isLoading, reload, setMessages } = useChat({
    api: '/api/chat',
    body: {
      sessionId: sessionIdRef.current,
      userPhone
    },
    onResponse: (response: any) => {
      const confidenceHeader = response.headers.get('X-Confidence')
      const sourceHeader = response.headers.get('X-Source')

      if (confidenceHeader) {
        setMetadata(prev => ({ ...prev, confidence: parseFloat(confidenceHeader) }))
      }
      if (sourceHeader) {
        setMetadata(prev => ({ ...prev, source: sourceHeader }))
      }
    },
    onError: (error: any) => {
      console.error('Chat error:', error);
    }
  } as any) as any;

  const [error, setError] = React.useState<string | null>(null)

  const [input, setInput] = React.useState('')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    // Removed isLoading check to prevent blocking if state gets stuck
    if (!input.trim()) return

    const message = input
    setInput('')
    setError(null) // Clear any previous errors

    try {
      await append({
        role: 'user',
        content: message
      }, {
        body: {
          data: {
            sessionId: sessionIdRef.current,
            userPhone
          }
        }
      })
    } catch (error) {
      console.error('Append failed:', error)
      setError('No se pudo enviar el mensaje. Por favor, intenta de nuevo.')
    }
  }

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: messages.length ? 'smooth' : 'auto' })
  }, [messages.length])

  useEffect(() => {
    scrollToBottom()
  }, [scrollToBottom])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K to focus input
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
      // Escape to clear input
      if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        setInput('')
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Save session to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chat_session', JSON.stringify({
        messages: messages.slice(-20), // Keep last 20 messages
        sessionId: sessionIdRef.current,
        timestamp: Date.now()
      }))
    }
  }, [messages])

  // Load session on mount
  useEffect(() => {
    const savedSession = localStorage.getItem('chat_session')
    if (savedSession) {
      try {
        const { messages: savedMessages, sessionId, timestamp } = JSON.parse(savedSession)
        // Only restore if less than 1 hour old
        if (Date.now() - timestamp < 3600000) {
          setMessages(savedMessages)
          sessionIdRef.current = sessionId
        }
      } catch (e) {
        console.error('Failed to restore session:', e)
      }
    }
  }, [])

  const handleNewChat = () => {
    setMessages([])
    setMetadata({})
    sessionIdRef.current = `session_${userPhone}_${Date.now()}`
    localStorage.removeItem('chat_session')
    inputRef.current?.focus()
  }

  const getMessageIcon = (role: string) => {
    switch (role) {
      case 'user': return <User className="w-4 h-4" />
      case 'assistant': return <Bot className="w-4 h-4" />
      case 'system': return <MessageSquare className="w-4 h-4" />
      default: return <MessageSquare className="w-4 h-4" />
    }
  }

  const getMessageColor = (role: string) => {
    switch (role) {
      case 'user': return 'bg-blue-100 text-blue-800'
      case 'assistant': return 'bg-green-100 text-green-800'
      case 'system': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Compact Header */}
      <div className="character-header mb-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <h2 className="text-xl font-bold bg-gradient-to-r from-cyan-600 to-yellow-600 bg-clip-text text-transparent">
              Asistente Virtual BMC
            </h2>
            <p className="text-xs text-muted-foreground">
              Chat con tu experto en construcción
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={handleNewChat}
            className="text-xs hover:bg-gradient-to-r hover:from-cyan-50 hover:to-yellow-50"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            Nueva Consulta
          </Button>
        </div>
      </div>

      {/* Character Scene with Messages */}
      <div className="flex-1 relative">
        <div className="character-scene h-full flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto chat-messages px-4 py-6" style={{ paddingBottom: '320px' }} role="log" aria-live="polite" aria-label="Historial de mensajes">
            {messages.length === 0 && (
              <div className="character-welcome">
                <h3 className="font-bold text-2xl mb-2 bg-gradient-to-r from-cyan-600 to-yellow-600 bg-clip-text text-transparent">
                  ¡Hola! Soy tu experto en construcción
                </h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto mb-8">
                  Puedo ayudarte con cotizaciones de Isodec, paneles, y responder todas tus dudas técnicas.
                  ¿En qué puedo ayudarte hoy?
                </p>
                <div className="grid grid-cols-1 gap-3 text-sm text-left max-w-md mx-auto">
                  <div
                    className="suggestion-chip"
                    onClick={() => append({ role: 'user', content: 'Cotizar 50m2 de Isodec 100mm' })}
                  >
                    💡 Cotizar 50m2 de Isodec 100mm
                  </div>
                  <div
                    className="suggestion-chip"
                    onClick={() => append({ role: 'user', content: '¿Qué diferencia hay entre Isodec y Lana de Roca?' })}
                  >
                    🤔 ¿Diferencia entre Isodec y Lana de Roca?
                  </div>
                </div>
              </div>
            )}

            {messages.map((message: any, index: number) => {
              const isLastAssistantMessage = message.role === 'assistant' && index === messages.length - 1;
              return (
                <MessageBubble
                  key={message.id}
                  role={message.role as 'user' | 'assistant' | 'system'}
                  content={message.content}
                  confidence={isLastAssistantMessage ? metadata.confidence : undefined}
                />
              )
            })}

            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="speech-bubble">
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground">Pensando</span>
                    <div className="pixel-dots">
                      <div className="pixel-dot"></div>
                      <div className="pixel-dot"></div>
                      <div className="pixel-dot"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Character Figure */}
        <div className="character-figure">
          <Image
            src="/images/character-scene.jpg"
            alt="Assistant Character"
            width={280}
            height={280}
            className="object-contain"
            priority
          />
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-sm text-red-800">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setError(null)}
            className="ml-auto h-6 px-2"
          >
            Cerrar
          </Button>
        </div>
      )}

      {/* Input */}
      <Card className="shadow-lg character-input" style={{ position: 'relative', zIndex: 20 }}>
        <CardContent className="p-3">
          <form onSubmit={handleSubmit} className="flex gap-2 items-center">
            <Input
              ref={inputRef}
              value={input}
              onChange={handleInputChange}
              placeholder="Escribe tu consulta aquí... (⌘K para enfocar)"
              disabled={isLoading}
              className="border-2 border-cyan-200 focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-0 rounded-xl px-4 py-2"
              autoFocus
              aria-label="Escribe tu mensaje"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.shiftKey) {
                  // Allow Shift+Enter for multiline (though Input doesn't support it, this prevents submit)
                  e.preventDefault()
                }
              }}
            />
            <Button
              type="submit"
              disabled={isLoading || !input.trim()}
              size="icon"
              className="h-10 w-10 bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 rounded-xl"
              aria-label="Enviar mensaje"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </CardContent>
      </Card>

    </div>
  )
}
