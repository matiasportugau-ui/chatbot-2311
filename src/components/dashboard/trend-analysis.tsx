import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  LineChart, 
  PieChart,
  Activity,
  Target,
  AlertTriangle
} from 'lucide-react'

interface TrendData {
  period: string
  value: number
  change: number
  changePercentage: number
}

interface TrendAnalysis {
  metric: string
  description: string
  currentValue: number
  previousValue: number
  change: number
  changePercentage: number
  trend: 'up' | 'down' | 'stable'
  confidence: number
  data: TrendData[]
  insights: string[]
  recommendations: string[]
}

interface TrendAnalysisProps {
  trends: TrendAnalysis[]
  className?: string
}

export function TrendAnalysis({ trends, className }: TrendAnalysisProps) {
  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(1)}%`
  }

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('es-UY').format(value)
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return TrendingUp
      case 'down': return TrendingDown
      default: return Activity
    }
  }

  const getTrendColor = (trend: string, change: number) => {
    if (trend === 'up' && change > 0) return 'text-green-500'
    if (trend === 'down' && change < 0) return 'text-red-500'
    return 'text-gray-500'
  }

  return (
    <div className={cn("space-y-6", className)}>
      {trends.map((trend, index) => {
        const TrendIcon = getTrendIcon(trend.trend)
        
        return (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendIcon className="h-5 w-5" />
                <span>{trend.metric}</span>
                <Badge variant={trend.trend === 'up' ? 'success' : trend.trend === 'down' ? 'destructive' : 'secondary'}>
                  {trend.trend.toUpperCase()}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Current vs Previous */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {formatNumber(trend.currentValue)}
                    </div>
                    <p className="text-sm text-muted-foreground">Current</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {formatNumber(trend.previousValue)}
                    </div>
                    <p className="text-sm text-muted-foreground">Previous</p>
                  </div>
                  <div className="text-center">
                    <div className={cn("text-2xl font-bold", getTrendColor(trend.trend, trend.change))}>
                      {formatPercentage(trend.changePercentage)}
                    </div>
                    <p className="text-sm text-muted-foreground">Change</p>
                  </div>
                </div>

                {/* Description */}
                <p className="text-sm text-muted-foreground">
                  {trend.description}
                </p>

                {/* Trend Data */}
                <div className="space-y-2">
                  <h4 className="font-medium">Trend Data</h4>
                  <div className="space-y-1">
                    {trend.data.map((dataPoint, dataIndex) => (
                      <div key={dataIndex} className="flex items-center justify-between text-sm">
                        <span>{dataPoint.period}</span>
                        <div className="flex items-center space-x-2">
                          <span>{formatNumber(dataPoint.value)}</span>
                          <span className={cn(
                            "text-xs",
                            dataPoint.change >= 0 ? "text-green-500" : "text-red-500"
                          )}>
                            {formatPercentage(dataPoint.changePercentage)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Insights */}
                <div className="space-y-2">
                  <h4 className="font-medium">Insights</h4>
                  <div className="space-y-1">
                    {trend.insights.map((insight, insightIndex) => (
                      <div key={insightIndex} className="flex items-start space-x-2 text-sm">
                        <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5" />
                        <span>{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div className="space-y-2">
                  <h4 className="font-medium">Recommendations</h4>
                  <div className="space-y-1">
                    {trend.recommendations.map((recommendation, recIndex) => (
                      <div key={recIndex} className="flex items-start space-x-2 text-sm">
                        <Target className="h-4 w-4 text-blue-500 mt-0.5" />
                        <span>{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Confidence Score */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Confidence Score</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-muted rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full" 
                        style={{ width: `${trend.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {(trend.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
