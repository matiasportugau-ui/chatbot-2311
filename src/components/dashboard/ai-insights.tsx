import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  Brain, 
  Lightbulb, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Target,
  Zap,
  BarChart3
} from 'lucide-react'

interface AIInsight {
  id: string
  type: 'prediction' | 'recommendation' | 'anomaly' | 'optimization'
  title: string
  description: string
  confidence: number
  impact: 'low' | 'medium' | 'high'
  urgency: 'low' | 'medium' | 'high'
  category: string
  metrics: string[]
  actionItems: string[]
  expectedOutcome: string
  timestamp: string
}

interface AIInsightsProps {
  insights: AIInsight[]
  className?: string
}

export function AIInsights({ insights, className }: AIInsightsProps) {
  const typeColors = {
    prediction: 'success',
    recommendation: 'warning',
    anomaly: 'destructive',
    optimization: 'secondary'
  } as const

  const typeIcons = {
    prediction: TrendingUp,
    recommendation: Lightbulb,
    anomaly: AlertTriangle,
    optimization: Target
  } as const

  const impactColors = {
    low: 'secondary',
    medium: 'warning',
    high: 'destructive'
  } as const

  const urgencyColors = {
    low: 'secondary',
    medium: 'warning',
    high: 'destructive'
  } as const

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-UY', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Brain className="h-5 w-5" />
          <span>AI Insights</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {insights.map((insight) => {
            const TypeIcon = typeIcons[insight.type]
            
            return (
              <Card key={insight.id} className="p-4">
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <TypeIcon className="h-4 w-4" />
                      <span className="font-medium">{insight.title}</span>
                      <Badge variant={typeColors[insight.type]}>
                        {insight.type.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={impactColors[insight.impact]}>
                        {insight.impact.toUpperCase()}
                      </Badge>
                      <Badge variant={urgencyColors[insight.urgency]}>
                        {insight.urgency.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-muted-foreground">
                    {insight.description}
                  </p>

                  {/* Confidence Score */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Confidence Score</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-muted rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full" 
                          style={{ width: `${insight.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {(insight.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="space-y-2">
                    <div className="flex items-center space-x-1">
                      <BarChart3 className="h-4 w-4" />
                      <span className="text-sm font-medium">Metrics Affected</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {insight.metrics.map((metric, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {metric}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Action Items */}
                  <div className="space-y-2">
                    <div className="flex items-center space-x-1">
                      <Target className="h-4 w-4" />
                      <span className="text-sm font-medium">Action Items</span>
                    </div>
                    <div className="space-y-1">
                      {insight.actionItems.map((item, index) => (
                        <div key={index} className="flex items-start space-x-2 text-sm">
                          <CheckCircle className="h-3 w-3 text-green-500 mt-0.5" />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Expected Outcome */}
                  <div className="space-y-2">
                    <div className="flex items-center space-x-1">
                      <Zap className="h-4 w-4" />
                      <span className="text-sm font-medium">Expected Outcome</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {insight.expectedOutcome}
                    </p>
                  </div>

                  {/* Timestamp */}
                  <div className="text-xs text-muted-foreground">
                    Generated: {formatDate(insight.timestamp)}
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline">
                      Implement
                    </Button>
                    <Button size="sm" variant="outline">
                      Dismiss
                    </Button>
                    <Button size="sm" variant="outline">
                      Learn More
                    </Button>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
