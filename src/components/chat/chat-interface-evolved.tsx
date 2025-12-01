'use client'

import React, { useEffect, useRef, useState, useCallback } from 'react'
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

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt?: Date
}

interface QuoteMetadata {
  tipo?: string
  confianza?: number
}

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
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [contextUsage, setContextUsage] = useState(0)
  const [quoteMetadata, setQuoteMetadata] = useState<QuoteMetadata | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Initialize session on mount
  useEffect(() => {
    if (!sessionId) {
      initializeSession()
    }
  }, [sessionId])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const initializeSession = async () => {
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
      }
    } catch (error) {
      console.error('Failed to initialize session:', error)
    }
  }

  const updateContextUsage = async () => {
    if (!sessionId) return
    
    try {
      const response = await fetch(`/api/context?action=get&sessionId=${sessionId}&userPhone=${userPhone}`)
      const data = await response.json()
      if (data.data?.token_count) {
        const maxTokens = 8000
        const usage = Math.min((data.data.token_count / maxTokens) * 100, 100)
        setContextUsage(usage)
      }
    } catch (error) {
      console.error('Failed to update context usage:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      createdAt: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          user_phone: userPhone,
          session_id: sessionId
        })
      })

      const data = await response.json()
      
      // Update session ID if provided
      if (data.session_id) {
        setSessionId(data.session_id)
      }

      // Update quote metadata if present
      if (data.quote_type) {
        setQuoteMetadata({
          tipo: data.quote_type,
          confianza: data.confidence || 0
        })
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || data.message || 'No response received',
        createdAt: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      updateContextUsage()
    } catch (err) {
      console.error('Chat error:', err)
      setError(err instanceof Error ? err : new Error('Failed to send message'))
    } finally {
      setIsLoading(false)
    }
  }

  // Minimum messages required for reload (user + assistant)
  const MIN_MESSAGES_FOR_RELOAD = 2

  const handleReload = async () => {
    if (messages.length < MIN_MESSAGES_FOR_RELOAD) return
    
    // Get last user message
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user')
    if (!lastUserMessage) return

    // Remove last assistant message
    const newMessages = messages.slice(0, -1)
    setMessages(newMessages)
    
    // Resend
    setInput(lastUserMessage.content)
    // The form will need to be submitted manually
  }

  const getIntentIcon = (intent?: string) => {
    switch (intent) {
      case 'quote_request':
        return <Calculator className="h-4 w-4" />
      case 'product_info':
        return <Info className="h-4 w-4" />
      case 'company_info':
        return <Building2 className="h-4 w-4" />
      default:
        return <MessageSquare className="h-4 w-4" />
    }
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Bot className="h-5 w-5 text-primary" />
            Chat de Cotizaciones BMC
          </CardTitle>
          <div className="flex items-center gap-2">
            {quoteMetadata && (
              <Badge variant="outline" className="flex items-center gap-1">
                {getIntentIcon(quoteMetadata.tipo)}
                {quoteMetadata.tipo}
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReload}
              disabled={isLoading || messages.length < 2}
              title="Regenerar última respuesta"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
        
        {/* Context Usage Indicator */}
        <div className="mt-2">
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>Contexto usado</span>
            <span>{Math.round(contextUsage)}%</span>
          </div>
          <Progress value={contextUsage} className="h-1" />
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Messages Area */}
        <div className="h-[400px] overflow-y-auto border rounded-lg p-4 space-y-4 bg-muted/30">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Inicia una conversación para cotizar productos de aislamiento térmico.</p>
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                  <Bot className="h-4 w-4 text-primary-foreground" />
                </div>
              )}
              
              <div className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user' 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-card border'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                {message.createdAt && (
                  <p className="text-xs opacity-70 mt-1">
                    {new Date(message.createdAt).toLocaleTimeString('es-UY', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                )}
              </div>
              
              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
              <div className="bg-card border rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 animate-pulse text-yellow-500" />
                  <span className="text-sm text-muted-foreground">Procesando...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex items-center gap-2 p-2 bg-destructive/10 text-destructive rounded-lg text-sm">
            <AlertTriangle className="h-4 w-4" />
            <span>{error.message}</span>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu mensaje..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInput('Necesito cotizar Isodec de 100mm')}
            disabled={isLoading}
          >
            <Calculator className="h-3 w-3 mr-1" />
            Cotizar Isodec
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInput('¿Qué productos tienen disponibles?')}
            disabled={isLoading}
          >
            <Info className="h-3 w-3 mr-1" />
            Ver productos
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInput('¿Dónde están ubicados?')}
            disabled={isLoading}
          >
            <Building2 className="h-3 w-3 mr-1" />
            Ubicación
          </Button>
        </div>

        {/* Session Info */}
        {sessionId && (
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <CheckCircle className="h-3 w-3 text-green-500" />
            Sesión: {sessionId.slice(0, 20)}...
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default ChatInterfaceEvolved
