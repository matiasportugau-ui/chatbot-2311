import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  Lightbulb, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Target,
  Zap
} from 'lucide-react'

interface ImprovementSuggestion {
  id: string
  category: string
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  expectedImpact: string
  implementationEffort: 'low' | 'medium' | 'high'
  confidenceScore: number
  status: 'pending' | 'in-progress' | 'completed' | 'rejected'
  metricsAffected: string[]
}

interface ImprovementSuggestionsProps {
  suggestions: ImprovementSuggestion[]
  className?: string
}

export function ImprovementSuggestions({ suggestions, className }: ImprovementSuggestionsProps) {
  const priorityColors = {
    high: 'destructive',
    medium: 'warning',
    low: 'secondary'
  } as const

  const priorityIcons = {
    high: AlertTriangle,
    medium: Clock,
    low: CheckCircle
  } as const

  const effortColors = {
    low: 'success',
    medium: 'warning',
    high: 'error'
  } as const

  const statusColors = {
    pending: 'secondary',
    'in-progress': 'warning',
    completed: 'success',
    rejected: 'destructive'
  } as const

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Lightbulb className="h-5 w-5" />
          <span>AI Improvement Suggestions</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {suggestions.map((suggestion) => {
            const PriorityIcon = priorityIcons[suggestion.priority]
            
            return (
              <Card key={suggestion.id} className="p-4">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <PriorityIcon className="h-4 w-4" />
                        <h4 className="font-semibold">{suggestion.title}</h4>
                        <Badge variant={priorityColors[suggestion.priority]}>
                          {suggestion.priority.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {suggestion.description}
                      </p>
                    </div>
                    <Badge variant={statusColors[suggestion.status]}>
                      {suggestion.status.replace('-', ' ').toUpperCase()}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="h-3 w-3" />
                        <span className="font-medium">Expected Impact</span>
                      </div>
                      <p className="text-muted-foreground">{suggestion.expectedImpact}</p>
                    </div>
                    
                    <div className="space-y-1">
                      <div className="flex items-center space-x-1">
                        <Target className="h-3 w-3" />
                        <span className="font-medium">Implementation Effort</span>
                      </div>
                      <Badge variant={effortColors[suggestion.implementationEffort]}>
                        {suggestion.implementationEffort.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <div className="space-y-1">
                      <div className="flex items-center space-x-1">
                        <Zap className="h-3 w-3" />
                        <span className="font-medium">Confidence</span>
                      </div>
                      <p className="text-muted-foreground">
                        {(suggestion.confidenceScore * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-1">
                      <span className="text-sm font-medium">Metrics Affected:</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {suggestion.metricsAffected.map((metric, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {metric}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline">
                      View Details
                    </Button>
                    <Button size="sm" variant="outline">
                      Implement
                    </Button>
                    <Button size="sm" variant="outline">
                      Dismiss
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
