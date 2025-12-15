import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { QuoteCard } from './quote-card'
import type { Quote, QuoteStatus } from '@/types/quote'
import { cn } from '@/lib/utils'

interface KanbanColumnProps {
  id: QuoteStatus
  title: string
  color: string
  quotes: Quote[]
}

export function KanbanColumn({ id, title, color, quotes }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id })

  const items = quotes.map((q) => q._id?.toString() || '')

  return (
    <div className="flex min-w-[320px] flex-col">
      <div className={cn('rounded-t-lg p-4', color)}>
        <h3 className="font-semibold">
          {title}
          <span className="ml-2 text-sm font-normal text-muted-foreground">
            ({quotes.length})
          </span>
        </h3>
      </div>

      <div
        ref={setNodeRef}
        className={cn(
          'flex-1 space-y-3 rounded-b-lg border-2 border-t-0 bg-muted/20 p-4 transition-colors',
          isOver && 'border-primary bg-primary/5'
        )}
        style={{ minHeight: '500px' }}
      >
        <SortableContext items={items} strategy={verticalListSortingStrategy}>
          {quotes.map((quote) => (
            <QuoteCard key={quote._id?.toString()} quote={quote} />
          ))}
        </SortableContext>

        {quotes.length === 0 && (
          <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
            No quotes in this column
          </div>
        )}
      </div>
    </div>
  )
}
