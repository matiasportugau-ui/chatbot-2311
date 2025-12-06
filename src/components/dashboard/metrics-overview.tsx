import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn, formatNumber, formatPercentage, getTrendColor, getTrendIcon } from '@/lib/utils'
import { 
  MessageSquare, 
  TrendingUp, 
  Clock, 
  Users, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Activity
} from 'lucide-react'

interface MetricsData {
  totalConversations: number
  successfulQuotes: number
  failedQuotes: number
  avgResponseTime: number
  conversionRate: number
  userSatisfaction: number
  systemUptime: number
  errorRate: number
}

interface MetricsOverviewProps {
  data: MetricsData
  className?: string
}

export function MetricsOverview({ data, className }: MetricsOverviewProps) {
  const metrics = [
    {
      title: 'Total Conversations',
      value: data.totalConversations,
      icon: MessageSquare,
      status: 'info' as const,
      description: 'Daily conversation volume'
    },
    {
      title: 'Conversion Rate',
      value: `${formatPercentage(data.conversionRate / 100)}`,
      icon: TrendingUp,
      status: data.conversionRate >= 40 ? 'success' : data.conversionRate >= 30 ? 'warning' : 'error' as const,
      description: 'Successful quote generation rate',
      progress: data.conversionRate
    },
    {
      title: 'Avg Response Time',
      value: `${data.avgResponseTime.toFixed(1)}s`,
      icon: Clock,
      status: data.avgResponseTime <= 3 ? 'success' : data.avgResponseTime <= 5 ? 'warning' : 'error' as const,
      description: 'Average response time'
    },
    {
      title: 'User Satisfaction',
      value: `${data.userSatisfaction.toFixed(1)}/10`,
      icon: Users,
      status: data.userSatisfaction >= 8 ? 'success' : data.userSatisfaction >= 6 ? 'warning' : 'error' as const,
      description: 'Average user satisfaction score',
      progress: data.userSatisfaction * 10
    },
    {
      title: 'System Uptime',
      value: `${data.systemUptime.toFixed(1)}%`,
      icon: Activity,
      status: data.systemUptime >= 99 ? 'success' : data.systemUptime >= 95 ? 'warning' : 'error' as const,
      description: 'System availability',
      progress: data.systemUptime
    },
    {
      title: 'Error Rate',
      value: `${formatPercentage(data.errorRate / 100)}`,
      icon: AlertTriangle,
      status: data.errorRate <= 5 ? 'success' : data.errorRate <= 10 ? 'warning' : 'error' as const,
      description: 'System error rate',
      progress: data.errorRate
    }
  ]

  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4", className)}>
      {metrics.map((metric, index) => (
        <Card key={index} className="card-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {metric.title}
            </CardTitle>
            <metric.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <span className="text-2xl font-bold">
                  {metric.value}
                </span>
                <Badge 
                  variant={metric.status === 'success' ? 'success' : metric.status === 'warning' ? 'warning' : 'error'}
                  className="text-xs"
                >
                  {metric.status === 'success' ? '✓' : metric.status === 'warning' ? '⚠' : '✗'}
                </Badge>
              </div>
              
              <p className="text-xs text-muted-foreground">
                {metric.description}
              </p>
              
              {metric.progress !== undefined && (
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>Progress</span>
                    <span>{formatPercentage(metric.progress / 100)}</span>
                  </div>
                  <Progress 
                    value={metric.progress} 
                    className="h-2"
                  />
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
