import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn, formatNumber, formatPercentage, getTrendColor, getTrendIcon } from '@/lib/utils'
import { LucideIcon } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string | number
  change?: number
  trend?: 'up' | 'down' | 'neutral'
  icon?: LucideIcon
  description?: string
  progress?: number
  status?: 'success' | 'warning' | 'error' | 'info'
  className?: string
}

export function KPICard({
  title,
  value,
  change,
  trend = 'neutral',
  icon: Icon,
  description,
  progress,
  status = 'info',
  className
}: KPICardProps) {
  const statusColors = {
    success: 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950',
    warning: 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950',
    error: 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950',
    info: 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950'
  }

  const iconColors = {
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600',
    info: 'text-blue-600'
  }

  return (
    <Card className={cn(
      "card-hover transition-all duration-200",
      statusColors[status],
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && (
          <Icon className={cn("h-4 w-4", iconColors[status])} />
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold">
              {typeof value === 'number' ? formatNumber(value) : value}
            </span>
            {change !== undefined && (
              <Badge 
                variant={trend === 'up' ? 'success' : trend === 'down' ? 'error' : 'secondary'}
                className="text-xs"
              >
                <span className={getTrendColor(trend)}>
                  {getTrendIcon(trend)} {formatPercentage(Math.abs(change) / 100)}
                </span>
              </Badge>
            )}
          </div>
          
          {description && (
            <p className="text-xs text-muted-foreground">
              {description}
            </p>
          )}
          
          {progress !== undefined && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Progress</span>
                <span>{formatPercentage(progress / 100)}</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
