/**
 * CRM Types and Interfaces
 * Type definitions for the Custom MongoDB CRM system
 */

import { ObjectId } from 'mongodb';

/**
 * Customer record
 */
export interface Customer {
  _id?: ObjectId;
  // Basic Information
  email: string;
  name: string;
  phone?: string;
  company?: string;

  // Address
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zipCode?: string;
    country?: string;
  };

  // Metadata
  tags: string[];
  source: 'quote' | 'mercadolibre' | 'manual' | 'import';
  status: 'lead' | 'prospect' | 'customer' | 'inactive';

  // Statistics
  stats: {
    totalQuotes: number;
    totalOrders: number;
    totalRevenue: number;
    lastContactDate?: Date;
    firstContactDate: Date;
  };

  // References
  mercadoLibreUserId?: string;
  mercadoLibreNickname?: string;

  // Custom fields (flexible schema)
  customFields?: Record<string, any>;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Interaction record (emails, calls, meetings, notes)
 */
export interface Interaction {
  _id?: ObjectId;
  customerId: ObjectId | string;

  // Interaction details
  type: 'email' | 'call' | 'meeting' | 'note' | 'whatsapp' | 'other';
  direction?: 'inbound' | 'outbound';
  subject?: string;
  content: string;

  // Email specific
  emailId?: string;
  emailTo?: string;
  emailFrom?: string;

  // Metadata
  tags: string[];
  attachments?: Array<{
    name: string;
    url: string;
    type: string;
  }>;

  // References
  quoteId?: string;
  orderId?: string;

  // Timestamps
  occurredAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Note attached to customer
 */
export interface Note {
  _id?: ObjectId;
  customerId: ObjectId | string;

  content: string;
  isPinned: boolean;
  tags: string[];

  createdBy?: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Quote linked to customer
 */
export interface CRMQuote {
  _id?: ObjectId;
  customerId: ObjectId | string;

  quoteNumber: string;
  items: Array<{
    name: string;
    quantity: number;
    unitPrice: number;
    total: number;
  }>;

  subtotal: number;
  iva: number;
  total: number;

  status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired';
  validUntil?: Date;

  // References
  emailSentAt?: Date;
  acceptedAt?: Date;

  createdAt: Date;
  updatedAt: Date;
}

/**
 * Customer creation input
 */
export interface CreateCustomerInput {
  email: string;
  name: string;
  phone?: string;
  company?: string;
  address?: Customer['address'];
  tags?: string[];
  source?: Customer['source'];
  status?: Customer['status'];
  mercadoLibreUserId?: string;
  mercadoLibreNickname?: string;
  customFields?: Record<string, any>;
}

/**
 * Customer update input
 */
export interface UpdateCustomerInput {
  name?: string;
  phone?: string;
  company?: string;
  address?: Customer['address'];
  tags?: string[];
  status?: Customer['status'];
  customFields?: Record<string, any>;
}

/**
 * Interaction creation input
 */
export interface CreateInteractionInput {
  customerId: string;
  type: Interaction['type'];
  direction?: Interaction['direction'];
  subject?: string;
  content: string;
  tags?: string[];
  quoteId?: string;
  orderId?: string;
  occurredAt?: Date;
}

/**
 * Note creation input
 */
export interface CreateNoteInput {
  customerId: string;
  content: string;
  isPinned?: boolean;
  tags?: string[];
}

/**
 * CRM statistics
 */
export interface CRMStats {
  totalCustomers: number;
  totalInteractions: number;
  totalRevenue: number;
  customersByStatus: {
    lead: number;
    prospect: number;
    customer: number;
    inactive: number;
  };
  customersBySource: {
    quote: number;
    mercadolibre: number;
    manual: number;
    import: number;
  };
  recentActivity: {
    date: string;
    count: number;
  }[];
}

/**
 * Customer search filters
 */
export interface CustomerSearchFilters {
  email?: string;
  name?: string;
  tags?: string[];
  status?: Customer['status'][];
  source?: Customer['source'][];
  minRevenue?: number;
  maxRevenue?: number;
  createdAfter?: Date;
  createdBefore?: Date;
}

/**
 * Customer with related data
 */
export interface CustomerWithRelations extends Customer {
  interactions?: Interaction[];
  notes?: Note[];
  quotes?: CRMQuote[];
  recentActivity?: Array<{
    type: 'interaction' | 'note' | 'quote' | 'order';
    date: Date;
    description: string;
  }>;
}
