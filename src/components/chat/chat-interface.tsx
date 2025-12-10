'use client'

import React, { useEffect, useRef } from 'react'
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
  RefreshCw
} from 'lucide-react'

interface ChatInterfaceProps {
  userPhone?: string
  className?: string
}

export function ChatInterface({ userPhone = '+59891234567', className }: ChatInterfaceProps) {
  const { messages, input, handleInputChange, handleSubmit, isLoading, reload, setMessages } = useChat({
    api: '/api/chat',
    body: {
      sessionId: `session_${userPhone}_${Date.now()}`,
      userPhone
    },
    onError: (error) => {
      console.error('Chat error:', error);
    }
  });

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
      {/* Header */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Chat de Cotizaciones (AI Powered)
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setMessages([])}
                className="text-xs"
              >
                <RefreshCw className="w-3 h-3 mr-1" />
                Nuevo Chat
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Messages */}
      <Card className="flex-1 mb-4">
        <CardContent className="p-4 h-96 overflow-y-auto">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-20">
                <Bot className="w-12 h-12 mx-auto mb-2 opacity-20" />
                <p>¡Hola! Soy tu asistente de cotizaciones.</p>
                <p className="text-sm">Pregúntame sobre Isodec, Poliestireno o Lana de Roca.</p>
              </div>
            )}

            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                role={message.role as 'user' | 'assistant' | 'system'}
                content={message.content}
              />
            ))}
            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-full bg-green-100 text-green-800">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="p-3 rounded-lg bg-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
                    <span className="text-sm">Escribiendo...</span>
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
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Escribe tu mensaje..."
              disabled={isLoading}
            />
            <Button
              type="submit"
              disabled={isLoading || !input.trim()}
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
