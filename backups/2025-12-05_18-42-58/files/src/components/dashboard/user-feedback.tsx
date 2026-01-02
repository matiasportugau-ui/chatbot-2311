import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  MessageSquare, 
  Star, 
  ThumbsUp, 
  ThumbsDown, 
  AlertCircle, 
  CheckCircle,
  Clock,
  User,
  Calendar
} from 'lucide-react'

interface UserFeedback {
  id: string
  user: string
  rating: number
  comment: string
  category: 'general' | 'bug' | 'feature' | 'improvement'
  priority: 'low' | 'medium' | 'high'
  status: 'new' | 'in-review' | 'in-progress' | 'resolved' | 'closed'
  timestamp: string
  response?: string
  tags: string[]
}

interface UserFeedbackProps {
  feedback: UserFeedback[]
  className?: string
}

export function UserFeedback({ feedback, className }: UserFeedbackProps) {
  const categoryColors = {
    general: 'secondary',
    bug: 'destructive',
    feature: 'success',
    improvement: 'warning'
  } as const

  const priorityColors = {
    low: 'secondary',
    medium: 'warning',
    high: 'destructive'
  } as const

  const statusColors = {
    new: 'secondary',
    'in-review': 'warning',
    'in-progress': 'warning',
    resolved: 'success',
    closed: 'destructive'
  } as const

  const getRatingStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, index) => (
      <Star
        key={index}
        className={cn(
          "h-4 w-4",
          index < rating ? "text-yellow-400 fill-current" : "text-gray-300"
        )}
      />
    ))
  }

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
          <MessageSquare className="h-5 w-5" />
          <span>User Feedback</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {feedback.map((item) => (
            <Card key={item.id} className="p-4">
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4" />
                    <span className="font-medium">{item.user}</span>
                    <Badge variant={categoryColors[item.category]}>
                      {item.category.toUpperCase()}
                    </Badge>
                    <Badge variant={priorityColors[item.priority]}>
                      {item.priority.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={statusColors[item.status]}>
                      {item.status.replace('-', ' ').toUpperCase()}
                    </Badge>
                    <div className="flex items-center space-x-1">
                      {getRatingStars(item.rating)}
                    </div>
                  </div>
                </div>

                {/* Comment */}
                <div className="space-y-2">
                  <p className="text-sm">{item.comment}</p>
                  {item.response && (
                    <div className="bg-muted p-3 rounded-md">
                      <div className="flex items-center space-x-2 mb-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-sm font-medium">Response</span>
                      </div>
                      <p className="text-sm">{item.response}</p>
                    </div>
                  )}
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {item.tags.map((tag, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>

                {/* Timestamp */}
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(item.timestamp)}</span>
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    Reply
                  </Button>
                  <Button size="sm" variant="outline">
                    Edit
                  </Button>
                  <Button size="sm" variant="outline">
                    Resolve
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
