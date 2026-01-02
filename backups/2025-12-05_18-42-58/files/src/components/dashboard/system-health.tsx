import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { 
  Activity, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Server, 
  Database,
  Cpu,
  HardDrive,
  Wifi,
  Shield
} from 'lucide-react'

interface SystemHealthMetric {
  name: string
  status: 'healthy' | 'warning' | 'critical' | 'offline'
  value: number
  maxValue: number
  unit: string
  description: string
  lastChecked: string
  trend: 'up' | 'down' | 'stable'
}

interface SystemHealthProps {
  metrics: SystemHealthMetric[]
  className?: string
}

export function SystemHealth({ metrics, className }: SystemHealthProps) {
  const statusColors = {
    healthy: 'success',
    warning: 'warning',
    critical: 'destructive',
    offline: 'secondary'
  } as const

  const statusIcons = {
    healthy: CheckCircle,
    warning: AlertTriangle,
    critical: XCircle,
    offline: XCircle
  } as const

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-500'
      case 'warning': return 'text-yellow-500'
      case 'critical': return 'text-red-500'
      case 'offline': return 'text-gray-500'
      default: return 'text-gray-500'
    }
  }

  const getProgressColor = (value: number, maxValue: number) => {
    const percentage = (value / maxValue) * 100
    if (percentage >= 90) return 'bg-red-500'
    if (percentage >= 80) return 'bg-yellow-500'
    if (percentage >= 70) return 'bg-orange-500'
    return 'bg-green-500'
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5" />
          <span>System Health</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {metrics.map((metric, index) => {
            const StatusIcon = statusIcons[metric.status]
            const percentage = (metric.value / metric.maxValue) * 100
            
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
                    {metric.value.toLocaleString()} / {metric.maxValue.toLocaleString()} {metric.unit}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="relative">
                    <Progress 
                      value={Math.min(percentage, 100)} 
                      className="h-2"
                    />
                    <div className="absolute inset-0 flex items-center justify-center text-xs font-medium">
                      {percentage.toFixed(1)}%
                    </div>
                  </div>
                  
                  <p className="text-xs text-muted-foreground">
                    {metric.description}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Last checked: {metric.lastChecked}</span>
                    <span className="capitalize">{metric.trend}</span>
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
