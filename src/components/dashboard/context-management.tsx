'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Database,
  Activity,
  Zap,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  MessageSquare,
  Settings,
  BarChart3,
  TrendingUp
} from 'lucide-react'

interface ContextManagementProps {
  className?: string
}

interface SessionData {
  sessionId: string
  userPhone: string
  currentIntent: string
  tokenCount: number
  messageCount: number
  lastActivity: string
  status: 'active' | 'archived' | 'error'
  contextSummary: string
}

interface ContextMetrics {
  totalSessions: number
  activeSessions: number
  avgTokensPerSession: number
  contextCompressions: number
  autoChatCreations: number
  contextEfficiency: number
  maxTokensReached: number
  avgSessionDuration: number
}

// Mock data for demonstration - moved outside component to avoid dependency issues
const MOCK_SESSIONS: SessionData[] = [
  {
    sessionId: 'sess_001',
    userPhone: '+59891234567',
    currentIntent: 'quote_request',
    tokenCount: 3200,
    messageCount: 15,
    lastActivity: '2024-12-19T10:30:00Z',
    status: 'active',
    contextSummary: 'Cliente interesado en paneles solares 2x3, necesita cotización urgente'
  },
  {
    sessionId: 'sess_002',
    userPhone: '+59898765432',
    currentIntent: 'product_inquiry',
    tokenCount: 1800,
    messageCount: 8,
    lastActivity: '2024-12-19T11:15:00Z',
    status: 'active',
    contextSummary: 'Consulta sobre inversores 3kW, comparando opciones'
  },
  {
    sessionId: 'sess_003',
    userPhone: '+59887654321',
    currentIntent: 'completed',
    tokenCount: 4500,
    messageCount: 22,
    lastActivity: '2024-12-19T09:45:00Z',
    status: 'archived',
    contextSummary: 'Cotización completada para sistema 5kW, cliente satisfecho'
  },
  {
    sessionId: 'sess_004',
    userPhone: '+59876543210',
    currentIntent: 'error',
    tokenCount: 0,
    messageCount: 0,
    lastActivity: '2024-12-19T08:20:00Z',
    status: 'error',
    contextSummary: 'Error en procesamiento de mensaje'
  }
]

export function ContextManagement({ className }: ContextManagementProps) {
  const [sessions, setSessions] = useState<SessionData[]>([])
  const [metrics, setMetrics] = useState<ContextMetrics>({
    totalSessions: 89,
    activeSessions: 8,
    avgTokensPerSession: 2450,
    contextCompressions: 12,
    autoChatCreations: 5,
    contextEfficiency: 87.3,
    maxTokensReached: 15,
    avgSessionDuration: 12.5
  })
  const [loading, setLoading] = useState(false)
  const [selectedSession, setSelectedSession] = useState<string | null>(null)



  useEffect(() => {
    setSessions(MOCK_SESSIONS)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'archived': return 'bg-blue-100 text-blue-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />
      case 'archived': return <Clock className="w-4 h-4" />
      case 'error': return <AlertTriangle className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  const getTokenUsageColor = (tokenCount: number) => {
    if (tokenCount > 7000) return 'text-red-600'
    if (tokenCount > 5000) return 'text-yellow-600'
    return 'text-green-600'
  }

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return 'Ahora'
    if (diffInMinutes < 60) return `${diffInMinutes}m`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`
    return `${Math.floor(diffInMinutes / 1440)}d`
  }

  const handleRefreshSessions = async () => {
    setLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setLoading(false)
  }

  const handleCompressContext = async (sessionId: string) => {
    // Simulate context compression
    setSessions(prev => prev.map(session =>
      session.sessionId === sessionId
        ? { ...session, tokenCount: Math.floor(session.tokenCount * 0.7) }
        : session
    ))
  }

  const handleCreateNewChat = async (sessionId: string) => {
    // Simulate new chat creation
    const newSession: SessionData = {
      sessionId: `sess_${Date.now()}`,
      userPhone: sessions.find(s => s.sessionId === sessionId)?.userPhone || '',
      currentIntent: 'new_conversation',
      tokenCount: 0,
      messageCount: 0,
      lastActivity: new Date().toISOString(),
      status: 'active',
      contextSummary: 'Nueva conversación iniciada'
    }
    setSessions(prev => [newSession, ...prev])
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Gestión de Contexto
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Monitoreo y optimización de sesiones de conversación
          </p>
        </div>
        <Button
          onClick={handleRefreshSessions}
          disabled={loading}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sesiones Totales</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totalSessions}</div>
            <p className="text-xs text-muted-foreground">
              +12% desde el mes pasado
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sesiones Activas</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{metrics.activeSessions}</div>
            <p className="text-xs text-muted-foreground">
              En tiempo real
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Promedio Tokens</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.avgTokensPerSession.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Por sesión
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Eficiencia Contexto</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{metrics.contextEfficiency}%</div>
            <p className="text-xs text-muted-foreground">
              Optimización
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Context Management Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Acciones de Gestión
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium">Compresiones de Contexto</h4>
              <div className="text-2xl font-bold text-orange-600">{metrics.contextCompressions}</div>
              <p className="text-sm text-muted-foreground">Últimas 24h</p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Chats Automáticos</h4>
              <div className="text-2xl font-bold text-purple-600">{metrics.autoChatCreations}</div>
              <p className="text-sm text-muted-foreground">Creados automáticamente</p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Límite Alcanzado</h4>
              <div className="text-2xl font-bold text-red-600">{metrics.maxTokensReached}</div>
              <p className="text-sm text-muted-foreground">Sesiones que alcanzaron 100%</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sessions List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Sesiones de Conversación
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sessions.map((session) => (
              <div
                key={session.sessionId}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${selectedSession === session.sessionId
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 hover:border-gray-300'
                  }`}
                onClick={() => setSelectedSession(
                  selectedSession === session.sessionId ? null : session.sessionId
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(session.status)}
                      <Badge className={getStatusColor(session.status)}>
                        {session.status}
                      </Badge>
                    </div>
                    <div>
                      <p className="font-medium">{session.userPhone}</p>
                      <p className="text-sm text-muted-foreground">
                        {session.sessionId}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className={`text-sm font-medium ${getTokenUsageColor(session.tokenCount)}`}>
                        {session.tokenCount.toLocaleString()} tokens
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {session.messageCount} mensajes
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">
                        {formatTimeAgo(session.lastActivity)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {session.currentIntent}
                      </p>
                    </div>
                  </div>
                </div>

                {selectedSession === session.sessionId && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="space-y-3">
                      <div>
                        <h4 className="font-medium text-sm mb-2">Resumen del Contexto:</h4>
                        <p className="text-sm text-muted-foreground">
                          {session.contextSummary}
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <div className="flex-1">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span>Uso de Tokens</span>
                            <span>{Math.round((session.tokenCount / 8000) * 100)}%</span>
                          </div>
                          <Progress
                            value={(session.tokenCount / 8000) * 100}
                            className="h-2"
                          />
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleCompressContext(session.sessionId)
                          }}
                          disabled={session.tokenCount < 5000}
                        >
                          <Zap className="w-3 h-3 mr-1" />
                          Comprimir
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleCreateNewChat(session.sessionId)
                          }}
                        >
                          <RefreshCw className="w-3 h-3 mr-1" />
                          Nuevo Chat
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Context Optimization Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Optimización de Contexto
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium">Recomendaciones Activas</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Compresión automática habilitada</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Creación automática de chats activa</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <AlertTriangle className="w-4 h-4 text-yellow-500" />
                  <span>Considerar aumentar límite de tokens</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">Estadísticas de Rendimiento</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Tiempo promedio de sesión:</span>
                  <span className="font-medium">{metrics.avgSessionDuration} min</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Eficiencia de contexto:</span>
                  <span className="font-medium text-green-600">{metrics.contextEfficiency}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Sesiones que necesitaron compresión:</span>
                  <span className="font-medium text-orange-600">{metrics.contextCompressions}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
