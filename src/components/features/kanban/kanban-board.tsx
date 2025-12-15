'use client'

import { useState } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import { KanbanColumn } from './kanban-column'
import { QuoteCard } from './quote-card'
import type { Quote, QuoteStatus } from '@/types/quote'

interface KanbanBoardProps {
  quotes: Quote[]
  onStatusChange: (quoteId: string, newStatus: QuoteStatus) => void
}

const columns: { id: QuoteStatus; title: string; color: string }[] = [
  { id: 'pending', title: 'Pending', color: 'bg-yellow-100 dark:bg-yellow-900/20' },
  { id: 'sent', title: 'Sent', color: 'bg-blue-100 dark:bg-blue-900/20' },
  { id: 'confirmed', title: 'Confirmed', color: 'bg-green-100 dark:bg-green-900/20' },
]

export function KanbanBoard({ quotes, onStatusChange }: KanbanBoardProps) {
  const [activeId, setActiveId] = useState<string | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      const quoteId = active.id as string
      const newStatus = over.id as QuoteStatus

      onStatusChange(quoteId, newStatus)
    }

    setActiveId(null)
  }

  const activeQuote = quotes.find((q) => q._id?.toString() === activeId)

  const getQuotesByStatus = (status: QuoteStatus) => {
    return quotes.filter((q) => q.status === status)
  }

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-6 overflow-x-auto pb-4">
        {columns.map((column) => (
          <KanbanColumn
            key={column.id}
            id={column.id}
            title={column.title}
            color={column.color}
            quotes={getQuotesByStatus(column.id)}
          />
        ))}
      </div>

      <DragOverlay>
        {activeQuote && (
          <div className="rotate-3 cursor-grabbing opacity-50">
            <QuoteCard quote={activeQuote} isDragging />
          </div>
        )}
      </DragOverlay>
    </DndContext>
  )
}
