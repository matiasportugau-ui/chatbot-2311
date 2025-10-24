'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
// import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { 
  MessageSquare, 
  Send, 
  RefreshCw, 
  // Compress, 
  PlusCircle,
  Calculator,
  Info,
  CheckCircle,
  AlertCircle,
  Building2,
  Phone,
  MapPin,
  Calendar
} from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    tipo?: 'cotizacion' | 'informacion' | 'pregunta' | 'error'
    cotizacion?: any
    productos_sugeridos?: any[]
    preguntas_frecuentes?: any[]
  }
}

interface ChatInterfaceProps {
  userPhone?: string
  className?: string
}

export function BMCChatInterface({ userPhone = '+59891234567', className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [contextTokens, setContextTokens] = useState(0)
  const [maxContextTokens] = useState(8000)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Inicializar sesión
  useEffect(() => {
    const newSessionId = `bmc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setSessionId(newSessionId)
    
    // Mensaje de bienvenida
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `¡Hola! 👋 Soy el asistente de BMC Construcciones.

Te puedo ayudar con:
🏗️ **Cotizaciones** - Paneles Isodec, Isoroof, chapas, calameria
ℹ️ **Información** - Sobre nuestros productos y servicios
📞 **Contacto** - Para consultas específicas

¿En qué te puedo ayudar hoy?`,
      timestamp: new Date(),
      metadata: { tipo: 'informacion' }
    }])
  }, [])

  // Auto-scroll al final
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Enviar mensaje
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          sessionId,
          userPhone
        })
      })

      const data = await response.json()
      
      if (data.success) {
        const assistantMessage: Message = {
          id: `assistant_${Date.now()}`,
          role: 'assistant',
          content: data.data.response.mensaje,
          timestamp: new Date(),
          metadata: {
            tipo: data.data.response.tipo,
            cotizacion: data.data.response.cotizacion,
            productos_sugeridos: data.data.response.productos_sugeridos,
            preguntas_frecuentes: data.data.response.preguntas_frecuentes
          }
        }

        setMessages(prev => [...prev, assistantMessage])
        
        // Actualizar tokens de contexto
        setContextTokens(prev => Math.min(maxContextTokens, prev + inputMessage.length / 4))
      } else {
        throw new Error(data.error || 'Error procesando mensaje')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'Lo siento, hubo un problema procesando tu mensaje. Por favor, intenta de nuevo.',
        timestamp: new Date(),
        metadata: { tipo: 'error' }
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Comprimir contexto
  const handleCompressContext = async () => {
    try {
      const response = await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'compress_context',
          session_id: sessionId
        })
      })

      if (response.ok) {
        setContextTokens(prev => Math.max(0, prev - 2000))
        
        const systemMessage: Message = {
          id: `system_compress_${Date.now()}`,
          role: 'system',
          content: 'Contexto comprimido automáticamente para optimizar el rendimiento.',
          timestamp: new Date()
        }
        
        setMessages(prev => [...prev, systemMessage])
      }
    } catch (error) {
      console.error('Error compressing context:', error)
    }
  }

  // Nuevo chat
  const handleNewChat = () => {
    const newSessionId = `bmc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setSessionId(newSessionId)
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `¡Hola! 👋 Soy el asistente de BMC Construcciones.

Te puedo ayudar con:
🏗️ **Cotizaciones** - Paneles Isodec, Isoroof, chapas, calameria
ℹ️ **Información** - Sobre nuestros productos y servicios
📞 **Contacto** - Para consultas específicas

¿En qué te puedo ayudar hoy?`,
      timestamp: new Date(),
      metadata: { tipo: 'informacion' }
    }])
    setContextTokens(0)
  }

  // Renderizar mensaje
  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user'
    const isSystem = message.role === 'system'
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
          <div className={`p-4 rounded-lg ${
            isUser 
              ? 'bg-primary text-primary-foreground' 
              : isSystem
                ? 'bg-secondary text-secondary-foreground text-sm italic'
                : 'bg-muted'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold capitalize">
                {isUser ? 'Tú' : isSystem ? 'Sistema' : 'Asistente BMC'}
              </span>
              {message.metadata?.tipo && (
                <Badge variant="outline" className="text-xs">
                  {message.metadata.tipo}
                </Badge>
              )}
            </div>
            
            <div className="whitespace-pre-wrap">{message.content}</div>
            
            {/* Mostrar cotización si existe */}
            {message.metadata?.cotizacion && (
              <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border">
                <div className="flex items-center gap-2 mb-2">
                  <Calculator className="w-4 h-4 text-green-600" />
                  <span className="font-semibold text-green-800 dark:text-green-200">
                    Cotización Generada
                  </span>
                </div>
                <div className="text-sm space-y-1">
                  <div><strong>Producto:</strong> {message.metadata.cotizacion.producto}</div>
                  <div><strong>Descripción:</strong> {message.metadata.cotizacion.descripcion}</div>
                  <div><strong>Precio Base:</strong> ${message.metadata.cotizacion.precio_base?.toLocaleString()}</div>
                  <div><strong>Total:</strong> ${message.metadata.cotizacion.total?.toLocaleString()}</div>
                  <div><strong>Código:</strong> {message.metadata.cotizacion.codigo}</div>
                </div>
              </div>
            )}
            
            {/* Mostrar productos sugeridos */}
            {message.metadata?.productos_sugeridos && message.metadata.productos_sugeridos.length > 0 && (
              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-blue-600" />
                  <span className="font-semibold text-blue-800 dark:text-blue-200">
                    Productos Sugeridos
                  </span>
                </div>
                {message.metadata.productos_sugeridos.map((producto: any, index: number) => (
                  <div key={index} className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-sm">
                    <div className="font-medium">{producto.nombre}</div>
                    <div className="text-gray-600 dark:text-gray-400">{producto.descripcion}</div>
                    <div className="text-green-600 font-medium">
                      ${producto.precio_estimado}/m²
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Mostrar preguntas frecuentes */}
            {message.metadata?.preguntas_frecuentes && message.metadata.preguntas_frecuentes.length > 0 && (
              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Info className="w-4 h-4 text-purple-600" />
                  <span className="font-semibold text-purple-800 dark:text-purple-200">
                    Preguntas Relacionadas
                  </span>
                </div>
                {message.metadata.preguntas_frecuentes.map((faq: any, index: number) => (
                  <div key={index} className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded text-sm">
                    <div className="font-medium">{faq.pregunta}</div>
                    <div className="text-gray-600 dark:text-gray-400">{faq.respuesta}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="text-xs text-gray-500 mt-1">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    )
  }

  const contextProgress = (contextTokens / maxContextTokens) * 100

  return (
    <Card className={`h-[calc(100vh-120px)] flex flex-col ${className}`}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-semibold flex items-center">
          <MessageSquare className="w-5 h-5 mr-2" />
          Chat BMC - {userPhone}
        </CardTitle>
        <div className="flex items-center space-x-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleCompressContext} 
            disabled={isLoading || contextProgress < 50}
          >
            <RefreshCw className="w-4 h-4 mr-1" /> Comprimir
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleNewChat} 
            disabled={isLoading}
          >
            <PlusCircle className="w-4 h-4 mr-1" /> Nuevo Chat
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="flex-grow flex flex-col p-0">
        <div className="flex-grow p-4 overflow-y-auto">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                Inicia una conversación para ver el historial.
              </div>
            )}
            {messages.map(renderMessage)}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] p-4 rounded-lg bg-muted">
                  <div className="font-semibold">Asistente BMC</div>
                  <div className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Procesando tu consulta...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        
        <div className="p-4 border-t">
          <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
            <span>Uso de Contexto: {contextTokens}/{maxContextTokens} tokens</span>
            <Badge variant={contextProgress > 80 ? 'destructive' : contextProgress > 50 ? 'warning' : 'secondary'}>
              {contextProgress.toFixed(1)}%
            </Badge>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div 
              className={`h-2 rounded-full transition-all ${
                contextProgress > 80 ? 'bg-red-500' : contextProgress > 50 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(100, contextProgress)}%` }}
            />
          </div>
          
          <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex space-x-2">
            <Input
              className="flex-grow"
              value={inputMessage}
              placeholder="Escribe tu consulta de cotización..."
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={isLoading}
            />
            <Button type="submit" disabled={isLoading || !inputMessage.trim()}>
              <Send className="w-4 h-4 mr-2" /> Enviar
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}
