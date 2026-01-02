import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  Activity, 
  Wifi, 
  WifiOff, 
  Server, 
  Database, 
  Cpu, 
  HardDrive,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw
} from 'lucide-react'

interface MonitoringMetric {
  name: string
  value: number
  unit: string
  status: 'online' | 'offline' | 'warning' | 'error'
  lastUpdate: string
  trend: 'up' | 'down' | 'stable'
  threshold: {
    warning: number
    critical: number
  }
}

interface RealTimeMonitoringProps {
  metrics: MonitoringMetric[]
  className?: string
}

export function RealTimeMonitoring({ metrics, className }: RealTimeMonitoringProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const refreshData = async () => {
    setIsRefreshing(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setLastRefresh(new Date())
    setIsRefreshing(false)
  }

  const statusColors = {
    online: 'success',
    offline: 'destructive',
    warning: 'warning',
    error: 'destructive'
  } as const

  const statusIcons = {
    online: CheckCircle,
    offline: WifiOff,
    warning: AlertTriangle,
    error: AlertTriangle
  } as const

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-500'
      case 'offline': return 'text-red-500'
      case 'warning': return 'text-yellow-500'
      case 'error': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getProgressColor = (value: number, threshold: { warning: number; critical: number }) => {
    if (value >= threshold.critical) return 'bg-red-500'
    if (value >= threshold.warning) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('es-UY', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>Real-time Monitoring</span>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={refreshData}
              disabled={isRefreshing}
            >
              <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
            </Button>
            <span className="text-xs text-muted-foreground">
              Last refresh: {lastRefresh.toLocaleTimeString()}
            </span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {metrics.map((metric, index) => {
            const StatusIcon = statusIcons[metric.status]
            const percentage = (metric.value / metric.threshold.critical) * 100
            
            return (
              <div key={index} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <StatusIcon className={cn("h-4 w-4", getStatusColor(metric.status))} />
                    <span className="font-medium">{metric.name}</span>
                    <Badge variant={statusColors[metric.status]}>
                      {metric.status.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {metric.value.toLocaleString()} {metric.unit}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="relative">
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className={cn(
                          "h-2 rounded-full transition-all duration-300",
                          getProgressColor(metric.value, metric.threshold)
                        )}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center text-xs font-medium">
                      {percentage.toFixed(1)}%
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Last update: {formatDate(metric.lastUpdate)}</span>
                    <span className="capitalize">{metric.trend}</span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span>Warning:</span>
                      <span>{metric.threshold.warning.toLocaleString()} {metric.unit}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Critical:</span>
                      <span>{metric.threshold.critical.toLocaleString()} {metric.unit}</span>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
