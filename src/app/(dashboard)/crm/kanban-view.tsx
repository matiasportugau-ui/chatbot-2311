'use client'

import { useState } from 'react'
import { KanbanBoard } from '@/components/features/kanban/kanban-board'
import type { Quote, QuoteStatus } from '@/types/quote'
import { ObjectId } from 'mongodb'

// Demo data for the Kanban board
const demoQuotes: Quote[] = [
  {
    _id: new ObjectId(),
    quoteNumber: 'Q-2024-001',
    customer: {
      id: '1',
      name: 'Juan Pérez',
      email: 'juan@example.com',
      phone: '+54 11 1234-5678',
      company: 'Empresa ABC',
    },
    items: [
      {
        id: '1',
        productName: 'Producto A',
        description: 'Descripción del producto',
        quantity: 10,
        unitPrice: 1500,
        subtotal: 15000,
      },
    ],
    subtotal: 15000,
    tax: 3150,
    discount: 0,
    total: 18150,
    status: 'pending',
    priority: 'high',
    notes: 'Cliente importante',
    validUntil: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    createdBy: 'user1',
    createdAt: new Date(),
    updatedAt: new Date(),
    tags: ['importante', 'urgente'],
  },
  {
    _id: new ObjectId(),
    quoteNumber: 'Q-2024-002',
    customer: {
      id: '2',
      name: 'María González',
      email: 'maria@example.com',
      company: 'Tech Solutions',
    },
    items: [
      {
        id: '1',
        productName: 'Servicio de Consultoría',
        quantity: 20,
        unitPrice: 2500,
        subtotal: 50000,
      },
    ],
    subtotal: 50000,
    tax: 10500,
    discount: 2500,
    total: 58000,
    status: 'sent',
    priority: 'medium',
    validUntil: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
    createdBy: 'user1',
    createdAt: new Date(),
    updatedAt: new Date(),
    sentAt: new Date(),
  },
  {
    _id: new ObjectId(),
    quoteNumber: 'Q-2024-003',
    customer: {
      id: '3',
      name: 'Carlos Rodríguez',
      email: 'carlos@example.com',
      phone: '+54 11 9876-5432',
    },
    items: [
      {
        id: '1',
        productName: 'Equipo de Hardware',
        quantity: 5,
        unitPrice: 8500,
        subtotal: 42500,
      },
    ],
    subtotal: 42500,
    tax: 8925,
    discount: 0,
    total: 51425,
    status: 'confirmed',
    priority: 'urgent',
    validUntil: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    createdBy: 'user1',
    createdAt: new Date(),
    updatedAt: new Date(),
    sentAt: new Date(),
    confirmedAt: new Date(),
    tags: ['hardware'],
  },
  {
    _id: new ObjectId(),
    quoteNumber: 'Q-2024-004',
    customer: {
      id: '4',
      name: 'Ana Martínez',
      email: 'ana@example.com',
      company: 'Innovación S.A.',
    },
    items: [
      {
        id: '1',
        productName: 'Licencias de Software',
        quantity: 15,
        unitPrice: 3200,
        subtotal: 48000,
      },
    ],
    subtotal: 48000,
    tax: 10080,
    discount: 4800,
    total: 53280,
    status: 'pending',
    priority: 'low',
    validUntil: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000),
    createdBy: 'user1',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
]

export function KanbanView() {
  const [quotes, setQuotes] = useState<Quote[]>(demoQuotes)

  const handleStatusChange = (quoteId: string, newStatus: QuoteStatus) => {
    setQuotes((prev) =>
      prev.map((quote) =>
        quote._id?.toString() === quoteId
          ? { ...quote, status: newStatus, updatedAt: new Date() }
          : quote
      )
    )
  }

  // Calculate stats
  const stats = {
    pending: quotes.filter((q) => q.status === 'pending').length,
    sent: quotes.filter((q) => q.status === 'sent').length,
    confirmed: quotes.filter((q) => q.status === 'confirmed').length,
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border bg-yellow-50 dark:bg-yellow-900/10 p-4">
          <div className="text-sm font-medium text-muted-foreground">
            Pending Quotes
          </div>
          <div className="text-2xl font-bold">{stats.pending}</div>
        </div>
        <div className="rounded-lg border bg-blue-50 dark:bg-blue-900/10 p-4">
          <div className="text-sm font-medium text-muted-foreground">
            Sent Quotes
          </div>
          <div className="text-2xl font-bold">{stats.sent}</div>
        </div>
        <div className="rounded-lg border bg-green-50 dark:bg-green-900/10 p-4">
          <div className="text-sm font-medium text-muted-foreground">
            Confirmed Orders
          </div>
          <div className="text-2xl font-bold">{stats.confirmed}</div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="rounded-lg border bg-card p-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold">Quote Pipeline</h2>
          <p className="text-sm text-muted-foreground">
            Drag and drop quotes between columns to update their status
          </p>
        </div>
        <KanbanBoard quotes={quotes} onStatusChange={handleStatusChange} />
      </div>
    </div>
  )
}
