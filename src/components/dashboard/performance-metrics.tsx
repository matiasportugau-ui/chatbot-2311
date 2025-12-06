import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  Activity, 
  Clock, 
  Zap, 
  Target, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react'

interface PerformanceMetric {
  name: string
  value: number
  target: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  status: 'excellent' | 'good' | 'warning' | 'critical'
  description: string
  lastUpdated: string
}

interface PerformanceMetricsProps {
  metrics: PerformanceMetric[]
  className?: string
}

export function PerformanceMetrics({ metrics, className }: PerformanceMetricsProps) {
  const statusColors = {
    excellent: 'success',
    good: 'success',
    warning: 'warning',
    critical: 'destructive'
  } as const

  const statusIcons = {
    excellent: CheckCircle,
    good: CheckCircle,
    warning: AlertCircle,
    critical: XCircle
  } as const

  const trendIcons = {
    up: TrendingUp,
    down: TrendingUp,
    stable: Activity
  } as const

  const getProgressColor = (value: number, target: number) => {
    const percentage = (value / target) * 100
    if (percentage >= 100) return 'bg-green-500'
    if (percentage >= 80) return 'bg-yellow-500'
    if (percentage >= 60) return 'bg-orange-500'
    return 'bg-red-500'
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5" />
          <span>Performance Metrics</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {metrics.map((metric, index) => {
            const StatusIcon = statusIcons[metric.status]
            const TrendIcon = trendIcons[metric.trend]
            const percentage = (metric.value / metric.target) * 100
            
            return (
              <div key={index} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <StatusIcon className="h-4 w-4" />
                    <span className="font-medium">{metric.name}</span>
                    <Badge variant={statusColors[metric.status]}>
                      {metric.status.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                    <TrendIcon className="h-3 w-3" />
                    <span>{metric.trend}</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>
                      {metric.value.toLocaleString()} {metric.unit}
                    </span>
                    <span className="text-muted-foreground">
                      Target: {metric.target.toLocaleString()} {metric.unit}
                    </span>
                  </div>
                  
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
                  
                  <p className="text-xs text-muted-foreground">
                    Last updated: {metric.lastUpdated}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
