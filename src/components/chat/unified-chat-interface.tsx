'use client'

import React, { useCallback, useEffect, useRef, useState } from 'react'
import { useChat } from '@ai-sdk/react'
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
    MessageSquare,
    Zap,
    Sparkles,
    ShieldCheck,
    Gauge,
    Info
} from 'lucide-react'

interface ChatInterfaceUnifiedProps {
    userPhone?: string
    className?: string
    sessionId?: string
}

interface QuoteMetadata {
    tipo?: string | null
    confianza?: number | null
}

const quickPrompts = [
    'Cotizar 120m² de Isodec 100mm para techo de galpón',
    '¿Qué diferencia hay entre Isodec y un panel de lana de roca?',
    'Necesito saber tiempos de entrega para Isoroof 50mm',
    'Ayúdame a comparar opciones de paneles para un depósito'
]

export function ChatInterfaceUnified({
    userPhone = '+59891234567',
    className,
    sessionId: initialSessionId
}: ChatInterfaceUnifiedProps) {
    const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null)
    const [contextUsage, setContextUsage] = useState(0)
    const [quoteMetadata, setQuoteMetadata] = useState<QuoteMetadata | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const sessionIdRef = useRef<string | null>(initialSessionId || null)
    const userPhoneRef = useRef<string>(userPhone)

    useEffect(() => {
        sessionIdRef.current = sessionId
    }, [sessionId])

    useEffect(() => {
        userPhoneRef.current = userPhone
    }, [userPhone])

    const updateContextUsage = useCallback(async () => {
        if (!sessionIdRef.current) return

        try {
            const response = await fetch('/api/context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'get_context',
                    session_id: sessionIdRef.current,
                    user_phone: userPhoneRef.current
                })
            })

            const data = await response.json()
            if (data.token_count) {
                setContextUsage(Math.min(100, (data.token_count / 8000) * 100))
            }
        } catch (error) {
            console.error('Error updating context usage:', error)
        }
    }, [])

    const {
        messages,
        input,
        handleInputChange,
        handleSubmit: originalHandleSubmit,
        isLoading,
        error,
        setMessages,
        append
    } = useChat({
        api: '/api/chat/stream',
        fetch: async (inputRequest: any, init: any) => {
            let requestBody: any = {}
            if (init?.body) {
                try {
                    requestBody = typeof init.body === 'string' ? JSON.parse(init.body) : init.body
                } catch (e) {
                    requestBody = {}
                }
            }

            requestBody.data = {
                userPhone: userPhoneRef.current,
                sessionId: sessionIdRef.current || undefined
            }

            return fetch(inputRequest, {
                ...init,
                headers: {
                    ...init?.headers,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            })
        },
        onResponse: (response: Response) => {
            const quoteType = response.headers.get('X-Quote-Type')
            const confidence = response.headers.get('X-Confidence')
            const sessionIdHeader = response.headers.get('X-Session-Id')

            if (sessionIdHeader) {
                setSessionId(sessionIdHeader)
                sessionIdRef.current = sessionIdHeader
            }

            if (quoteType) {
                let confianzaValue: number | null = null
                if (confidence) {
                    const parsed = parseFloat(confidence)
                    if (!isNaN(parsed) && isFinite(parsed) && parsed >= 0 && parsed <= 1) {
                        confianzaValue = parsed
                    }
                }

                setQuoteMetadata({
                    tipo: quoteType,
                    confianza: confianzaValue
                })
            }
        },
        onError: (err: Error) => {
            console.error('Chat error:', err)
        },
        onFinish: () => {
            updateContextUsage()
        }
    } as any) as any

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

                if (messages.length === 0) {
                    setMessages([
                        {
                            id: 'welcome',
                            role: 'assistant',
                            content:
                                '¡Hola! Soy tu asistente de cotizaciones de BMC Construcciones. ¿En qué puedo ayudarte hoy?'
                        }
                    ])
                }
            }
        } catch (err) {
            console.error('Error initializing session:', err)
        }
    }, [messages.length, setMessages, userPhone])

    useEffect(() => {
        if (!sessionId) {
            initializeSession()
        }
    }, [sessionId, initializeSession])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleCustomSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        if (!sessionIdRef.current || !(input || '').trim()) return

        try {
            await fetch('/api/context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'add_message',
                    session_id: sessionIdRef.current,
                    user_phone: userPhoneRef.current,
                    message: input,
                    message_type: 'user',
                    intent: 'user_input'
                })
            })
        } catch (err) {
            console.error('Error saving message:', err)
        }

        originalHandleSubmit(e)
    }

    const handleQuickPrompt = async (prompt: string) => {
        if (!sessionIdRef.current) return

        try {
            await fetch('/api/context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'add_message',
                    session_id: sessionIdRef.current,
                    user_phone: userPhoneRef.current,
                    message: prompt,
                    message_type: 'user',
                    intent: 'quick_prompt'
                })
            })

            await append(
                {
                    role: 'user',
                    content: prompt
                },
                {
                    body: {
                        data: {
                            userPhone: userPhoneRef.current,
                            sessionId: sessionIdRef.current
                        }
                    }
                }
            )

            handleInputChange({ target: { value: '' } } as any)
        } catch (err) {
            console.error('Error sending quick prompt:', err)
        }
    }

    const handleCompressContext = async () => {
        if (!sessionIdRef.current) return

        try {
            const response = await fetch('/api/context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'compress_context',
                    session_id: sessionIdRef.current
                })
            })

            const data = await response.json()
            if (data.success) {
                updateContextUsage()
            }
        } catch (err) {
            console.error('Error compressing context:', err)
        }
    }

    const handleNewChat = async () => {
        setMessages([])
        setQuoteMetadata(null)
        setContextUsage(0)
        setSessionId(null)
        sessionIdRef.current = null
        await initializeSession()
    }

    const getMessageIcon = (role: string) => {
        switch (role) {
            case 'user':
                return <User className="w-4 h-4" />
            case 'assistant':
                return <Bot className="w-4 h-4" />
            default:
                return <MessageSquare className="w-4 h-4" />
        }
    }

    const getMessageColor = (role: string) => {
        switch (role) {
            case 'user':
                return 'bg-blue-100 text-blue-800'
            case 'assistant':
                return 'bg-green-100 text-green-800'
            default:
                return 'bg-yellow-100 text-yellow-800'
        }
    }

    return (
        <div className={`flex flex-col h-full ${className || ''}`}>
            <Card className="mb-4">
                <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-3 flex-wrap">
                        <div>
                            <CardTitle className="flex items-center gap-2 text-xl">
                                <Sparkles className="w-5 h-5 text-cyan-600" />
                                Chat Unificado de Cotizaciones
                            </CardTitle>
                            <p className="text-sm text-muted-foreground">
                                Streaming, seguimiento de contexto y panel de confianza en una sola experiencia.
                            </p>
                        </div>
                        <div className="flex items-center gap-2 flex-wrap justify-end">
                            {sessionId && (
                                <Badge variant="outline" className="text-xs">
                                    Sesión {sessionId.slice(0, 10)}...
                                </Badge>
                            )}
                            {quoteMetadata?.tipo && (
                                <Badge variant="outline" className="text-xs">
                                    {quoteMetadata.tipo}
                                </Badge>
                            )}
                            {quoteMetadata?.confianza !== null && quoteMetadata?.confianza !== undefined && (
                                <Badge variant="secondary" className="text-xs">
                                    Confianza {(quoteMetadata.confianza * 100).toFixed(1)}%
                                </Badge>
                            )}
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                        <Gauge className="w-4 h-4 text-cyan-600" />
                        <span>Uso de contexto</span>
                        <Badge variant={contextUsage > 80 ? 'destructive' : contextUsage > 60 ? 'warning' : 'secondary'}>
                            {Math.round(contextUsage)}%
                        </Badge>
                    </div>
                    <Progress value={contextUsage} className="h-2" />
                    <div className="flex items-center gap-2 flex-wrap">
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={handleCompressContext}
                            disabled={isLoading || !sessionId}
                            className="text-xs"
                        >
                            <Zap className="w-3 h-3 mr-1" />
                            Comprimir
                        </Button>
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={handleNewChat}
                            disabled={isLoading}
                            className="text-xs"
                        >
                            <RefreshCw className="w-3 h-3 mr-1" />
                            Nuevo Chat
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {error && (
                <Card className="mb-4 border-red-200 bg-red-50">
                    <CardContent className="p-3 flex items-center gap-2 text-sm text-red-800">
                        <AlertTriangle className="w-4 h-4" />
                        <span>{error.message || 'Error procesando tu mensaje. Intenta nuevamente.'}</span>
                    </CardContent>
                </Card>
            )}

            <Card className="flex-1 mb-4">
                <CardContent className="p-4 h-[520px] overflow-y-auto">
                    <div className="space-y-4">
                        {messages.length === 0 && (
                            <div className="text-center text-muted-foreground space-y-3">
                                <p className="text-base font-medium">Inicia una conversación o usa un atajo.</p>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                    {quickPrompts.map(prompt => (
                                        <button
                                            key={prompt}
                                            onClick={() => handleQuickPrompt(prompt)}
                                            className="p-3 text-left rounded-lg border hover:border-cyan-400 hover:bg-cyan-50 transition text-sm"
                                        >
                                            {prompt}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {messages.map((message: any) => (
                            <div
                                key={message.id}
                                className={`flex items-start gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                            >
                                <div className={`p-2 rounded-full ${getMessageColor(message.role)}`}>
                                    {getMessageIcon(message.role)}
                                </div>
                                <div className={`flex-1 max-w-xl ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                                    <div
                                        className={`p-3 rounded-xl shadow-sm ${message.role === 'user'
                                                ? 'bg-cyan-600 text-white'
                                                : message.role === 'assistant'
                                                    ? 'bg-white border'
                                                    : 'bg-amber-50 border border-amber-100'
                                            }`}
                                    >
                                        <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                                        {message.role === 'assistant' && quoteMetadata?.confianza !== null && quoteMetadata?.confianza !== undefined && (
                                            <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                                                <ShieldCheck className="w-4 h-4" />
                                                Confianza {(quoteMetadata.confianza * 100).toFixed(1)}%
                                            </div>
                                        )}
                                    </div>
                                    {message.createdAt && (
                                        <p className="text-xs text-muted-foreground mt-1">
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
                                <div className="p-3 rounded-xl bg-white border shadow-sm flex items-center gap-2 text-sm">
                                    <RefreshCw className="w-4 h-4 animate-spin text-cyan-600" />
                                    Generando respuesta...
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <form onSubmit={handleCustomSubmit} className="flex gap-2 items-center">
                        <Input
                            value={input}
                            onChange={handleInputChange}
                            placeholder="Escribe tu mensaje de cotización o consulta..."
                            disabled={isLoading || !sessionId}
                            className="flex-1"
                        />
                        <Button
                            type="submit"
                            disabled={isLoading || !(input || '').trim() || !sessionId}
                            className="px-4"
                        >
                            <Send className="w-4 h-4" />
                        </Button>
                    </form>
                    <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                        <Info className="w-3 h-3" />
                        Usa los atajos para enviar consultas frecuentes más rápido.
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
