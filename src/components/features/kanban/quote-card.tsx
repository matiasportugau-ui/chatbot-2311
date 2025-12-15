import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Calendar, DollarSign, User, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { Quote } from '@/types/quote'
import { cn } from '@/lib/utils'

interface QuoteCardProps {
  quote: Quote
  isDragging?: boolean
}

export function QuoteCard({ quote, isDragging }: QuoteCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSorting,
  } = useSortable({ id: quote._id?.toString() || '' })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'error'
      case 'high':
        return 'warning'
      case 'medium':
        return 'default'
      case 'low':
        return 'secondary'
      default:
        return 'default'
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(amount)
  }

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('es-AR', {
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={cn(
        'touch-none',
        (isSorting || isDragging) && 'cursor-grabbing opacity-50'
      )}
    >
      <Card className="cursor-grab hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <div className="font-semibold text-sm">
                #{quote.quoteNumber}
              </div>
              <div className="text-sm font-medium mt-1">
                {quote.customer.name}
              </div>
              {quote.customer.company && (
                <div className="text-xs text-muted-foreground">
                  {quote.customer.company}
                </div>
              )}
            </div>
            <Badge variant={getPriorityColor(quote.priority)}>
              {quote.priority}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <DollarSign className="h-4 w-4 text-muted-foreground" />
            <span className="font-semibold">{formatCurrency(quote.total)}</span>
          </div>

          {quote.assignedTo && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>Assigned</span>
            </div>
          )}

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>Valid until {formatDate(quote.validUntil)}</span>
          </div>

          {new Date(quote.validUntil) < new Date() && (
            <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
              <AlertCircle className="h-4 w-4" />
              <span>Expired</span>
            </div>
          )}

          {quote.tags && quote.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {quote.tags.slice(0, 2).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {quote.tags.length > 2 && (
                <Badge variant="outline" className="text-xs">
                  +{quote.tags.length - 2}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
