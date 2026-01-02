'use client'

import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  Bell, 
  BellOff, 
  Settings, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  X,
  Filter
} from 'lucide-react'

interface Notification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
  category: 'system' | 'user' | 'ai' | 'performance'
  priority: 'low' | 'medium' | 'high'
  action?: {
    label: string
    onClick: () => void
  }
}

interface WebhookEvent {
  _id?: string
  topic?: string
  resource?: string
  receivedAt?: string
}

interface NotificationsProps {
  className?: string
}

const topicMapping: Record<string, { type: Notification['type']; priority: Notification['priority'] }> =
  {
    orders: { type: 'info', priority: 'medium' },
    items: { type: 'success', priority: 'low' },
    shipments: { type: 'warning', priority: 'high' }
  }

export function Notifications({ className }: NotificationsProps) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [filter, setFilter] = useState<'all' | 'unread' | 'system' | 'user' | 'ai' | 'performance'>('all')
  const [showSettings, setShowSettings] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const hydrateFromEvents = (events: WebhookEvent[]): Notification[] => {
    return events.map((event) => {
      const mapping = topicMapping[event.topic || ''] || { type: 'info', priority: 'low' }
      return {
        id: event._id?.toString() || `${event.topic}-${event.resource}-${event.receivedAt}`,
        type: mapping.type,
        title: `Evento ${event.topic || 'Mercado Libre'}`,
        message: `Actualización en ${event.resource || 'recurso desconocido'}`,
        timestamp: event.receivedAt || new Date().toISOString(),
        read: false,
        category: 'system',
        priority: mapping.priority
      }
    })
  }

  const loadEvents = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/mercado-libre/webhook?events=true')
      if (!response.ok) {
        throw new Error('No se pudieron obtener las notificaciones')
      }
      const data = await response.json()
      const events = hydrateFromEvents(data.events || [])
      setNotifications(events)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadEvents()
    const interval = setInterval(loadEvents, 30000)
    return () => clearInterval(interval)
  }, [])

  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true
    if (filter === 'unread') return !notification.read
    return notification.category === filter
  })

  const unreadCount = notifications.filter(n => !n.read).length

  const typeColors = {
    success: 'success',
    warning: 'warning',
    error: 'destructive',
    info: 'secondary'
  } as const

  const typeIcons = {
    success: CheckCircle,
    warning: AlertTriangle,
    error: AlertTriangle,
    info: Info
  } as const

  const priorityColors = {
    low: 'secondary',
    medium: 'warning',
    high: 'destructive'
  } as const

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  const markAsRead = (id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)))
  }

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <span>Notifications</span>
            {unreadCount > 0 && (
              <Badge variant="destructive">{unreadCount}</Badge>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={markAllAsRead}
              disabled={unreadCount === 0}
            >
              Mark All Read
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {error && (
            <div className="rounded bg-red-50 text-red-700 px-4 py-2 text-sm">{error}</div>
          )}

          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
              className="p-2 border rounded-lg text-sm"
            >
              <option value="all">All</option>
              <option value="unread">Unread</option>
              <option value="system">System</option>
              <option value="user">User</option>
              <option value="ai">AI</option>
              <option value="performance">Performance</option>
            </select>
          </div>

          <div className="space-y-3">
            {loading && notifications.length === 0 && (
              <div className="text-sm text-muted-foreground">Cargando notificaciones...</div>
            )}

            {filteredNotifications.map((notification) => {
              const TypeIcon = typeIcons[notification.type]
              
              return (
                <div
                  key={notification.id}
                  className={cn(
                    "p-4 border rounded-lg transition-colors",
                    !notification.read && "bg-muted/50 border-primary/20"
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <TypeIcon className={cn(
                        "h-4 w-4 mt-0.5",
                        typeColors[notification.type] === 'success' && "text-green-500",
                        typeColors[notification.type] === 'warning' && "text-yellow-500",
                        typeColors[notification.type] === 'destructive' && "text-red-500",
                        typeColors[notification.type] === 'secondary' && "text-blue-500"
                      )} />
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium">{notification.title}</h4>
                          <Badge variant={typeColors[notification.type]}>
                            {notification.type.toUpperCase()}
                          </Badge>
                          <Badge variant={priorityColors[notification.priority]}>
                            {notification.priority.toUpperCase()}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {notification.message}
                        </p>
                        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                          <span>{formatDate(notification.timestamp)}</span>
                          <span>•</span>
                          <span className="capitalize">{notification.category}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {!notification.read && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => markAsRead(notification.id)}
                        >
                          Mark Read
                        </Button>
                      )}
                      {notification.action && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={notification.action.onClick}
                        >
                          {notification.action.label}
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {showSettings && (
            <Card className="p-4">
              <div className="space-y-4">
                <h4 className="font-medium">Notification Settings</h4>
                <div className="space-y-3">
                  {[
                    { category: 'System', description: 'System health and updates' },
                    { category: 'User', description: 'User feedback and interactions' },
                    { category: 'AI', description: 'AI insights and recommendations' },
                    { category: 'Performance', description: 'Performance metrics and alerts' }
                  ].map((setting) => (
                    <div key={setting.category} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{setting.category}</p>
                        <p className="text-sm text-muted-foreground">{setting.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input type="checkbox" defaultChecked className="rounded" />
                        <span className="text-sm">Email</span>
                        <input type="checkbox" defaultChecked className="rounded" />
                        <span className="text-sm">Push</span>
                      </div>
                    </div>
                  ))}
                </div>
                <Button className="w-full">Save Settings</Button>
              </div>
            </Card>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
