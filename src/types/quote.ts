import { ObjectId } from 'mongodb'

/**
 * Quote status matching the Kanban columns
 */
export type QuoteStatus = 'pending' | 'sent' | 'confirmed' | 'rejected' | 'archived'

/**
 * Quote priority levels
 */
export type QuotePriority = 'low' | 'medium' | 'high' | 'urgent'

/**
 * Quote item in a quote
 */
export interface QuoteItem {
  id: string
  productId?: string
  productName: string
  description?: string
  quantity: number
  unitPrice: number
  discount?: number
  subtotal: number
}

/**
 * Customer information
 */
export interface Customer {
  id: string
  name: string
  email: string
  phone?: string
  company?: string
  address?: string
}

/**
 * Quote document
 */
export interface Quote {
  _id?: ObjectId
  quoteNumber: string
  customer: Customer
  items: QuoteItem[]
  subtotal: number
  tax: number
  discount: number
  total: number
  status: QuoteStatus
  priority: QuotePriority
  notes?: string
  internalNotes?: string
  validUntil: Date
  createdBy: string // User ID
  assignedTo?: string // User ID
  createdAt: Date
  updatedAt: Date
  sentAt?: Date
  confirmedAt?: Date
  rejectedAt?: Date
  tags?: string[]
}

/**
 * Create quote input
 */
export interface CreateQuoteInput {
  customer: Omit<Customer, 'id'>
  items: Omit<QuoteItem, 'id' | 'subtotal'>[]
  discount?: number
  notes?: string
  internalNotes?: string
  validUntil: Date
  priority?: QuotePriority
  assignedTo?: string
  tags?: string[]
}

/**
 * Update quote input
 */
export interface UpdateQuoteInput {
  customer?: Partial<Customer>
  items?: QuoteItem[]
  discount?: number
  notes?: string
  internalNotes?: string
  validUntil?: Date
  status?: QuoteStatus
  priority?: QuotePriority
  assignedTo?: string
  tags?: string[]
}

/**
 * Safe quote (for client)
 */
export interface SafeQuote extends Omit<Quote, '_id'> {
  id: string
}

/**
 * Quote statistics
 */
export interface QuoteStats {
  total: number
  pending: number
  sent: number
  confirmed: number
  rejected: number
  totalValue: number
  averageValue: number
}
