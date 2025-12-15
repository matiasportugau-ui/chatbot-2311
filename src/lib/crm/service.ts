/**
 * CRM Service Layer
 * Database operations for the Custom MongoDB CRM system
 */

import { ObjectId } from 'mongodb';
import { getMongoClient } from '@/lib/mongodb';
import type {
  Customer,
  Interaction,
  Note,
  CRMQuote,
  CreateCustomerInput,
  UpdateCustomerInput,
  CreateInteractionInput,
  CreateNoteInput,
  CustomerSearchFilters,
  CustomerWithRelations,
  CRMStats,
} from './types';

const CUSTOMERS_COLLECTION = 'crm_customers';
const INTERACTIONS_COLLECTION = 'crm_interactions';
const NOTES_COLLECTION = 'crm_notes';
const QUOTES_COLLECTION = 'crm_quotes';

/**
 * Get MongoDB collections
 */
async function getCollections() {
  const client = await getMongoClient();
  const db = client.db();

  return {
    customers: db.collection<Customer>(CUSTOMERS_COLLECTION),
    interactions: db.collection<Interaction>(INTERACTIONS_COLLECTION),
    notes: db.collection<Note>(NOTES_COLLECTION),
    quotes: db.collection<CRMQuote>(QUOTES_COLLECTION),
  };
}

// ============================================================================
// CUSTOMER OPERATIONS
// ============================================================================

/**
 * Create a new customer
 */
export async function createCustomer(input: CreateCustomerInput): Promise<Customer> {
  const { customers } = await getCollections();

  // Check if customer already exists
  const existing = await customers.findOne({ email: input.email.toLowerCase() });
  if (existing) {
    throw new Error(`Customer with email ${input.email} already exists`);
  }

  const customer: Customer = {
    email: input.email.toLowerCase(),
    name: input.name,
    phone: input.phone,
    company: input.company,
    address: input.address,
    tags: input.tags || [],
    source: input.source || 'manual',
    status: input.status || 'lead',
    stats: {
      totalQuotes: 0,
      totalOrders: 0,
      totalRevenue: 0,
      firstContactDate: new Date(),
    },
    mercadoLibreUserId: input.mercadoLibreUserId,
    mercadoLibreNickname: input.mercadoLibreNickname,
    customFields: input.customFields || {},
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const result = await customers.insertOne(customer);
  customer._id = result.insertedId;

  return customer;
}

/**
 * Get or create customer by email
 */
export async function getOrCreateCustomer(input: CreateCustomerInput): Promise<Customer> {
  const { customers } = await getCollections();

  const existing = await customers.findOne({ email: input.email.toLowerCase() });
  if (existing) {
    return existing;
  }

  return await createCustomer(input);
}

/**
 * Get customer by ID
 */
export async function getCustomerById(id: string): Promise<Customer | null> {
  const { customers } = await getCollections();
  return await customers.findOne({ _id: new ObjectId(id) });
}

/**
 * Get customer by email
 */
export async function getCustomerByEmail(email: string): Promise<Customer | null> {
  const { customers } = await getCollections();
  return await customers.findOne({ email: email.toLowerCase() });
}

/**
 * Update customer
 */
export async function updateCustomer(
  id: string,
  input: UpdateCustomerInput
): Promise<Customer | null> {
  const { customers } = await getCollections();

  const result = await customers.findOneAndUpdate(
    { _id: new ObjectId(id) },
    {
      $set: {
        ...input,
        updatedAt: new Date(),
      },
    },
    { returnDocument: 'after' }
  );

  return result || null;
}

/**
 * Delete customer
 */
export async function deleteCustomer(id: string): Promise<boolean> {
  const { customers, interactions, notes } = await getCollections();

  // Delete customer and all related data
  await Promise.all([
    customers.deleteOne({ _id: new ObjectId(id) }),
    interactions.deleteMany({ customerId: id }),
    notes.deleteMany({ customerId: id }),
  ]);

  return true;
}

/**
 * Search customers
 */
export async function searchCustomers(
  filters: CustomerSearchFilters = {},
  options: { limit?: number; offset?: number; sortBy?: string; sortOrder?: 'asc' | 'desc' } = {}
): Promise<{ customers: Customer[]; total: number }> {
  const { customers: collection } = await getCollections();

  // Build query
  const query: any = {};

  if (filters.email) {
    query.email = { $regex: filters.email, $options: 'i' };
  }

  if (filters.name) {
    query.name = { $regex: filters.name, $options: 'i' };
  }

  if (filters.tags && filters.tags.length > 0) {
    query.tags = { $in: filters.tags };
  }

  if (filters.status && filters.status.length > 0) {
    query.status = { $in: filters.status };
  }

  if (filters.source && filters.source.length > 0) {
    query.source = { $in: filters.source };
  }

  if (filters.minRevenue !== undefined || filters.maxRevenue !== undefined) {
    query['stats.totalRevenue'] = {};
    if (filters.minRevenue !== undefined) {
      query['stats.totalRevenue'].$gte = filters.minRevenue;
    }
    if (filters.maxRevenue !== undefined) {
      query['stats.totalRevenue'].$lte = filters.maxRevenue;
    }
  }

  if (filters.createdAfter || filters.createdBefore) {
    query.createdAt = {};
    if (filters.createdAfter) {
      query.createdAt.$gte = filters.createdAfter;
    }
    if (filters.createdBefore) {
      query.createdAt.$lte = filters.createdBefore;
    }
  }

  // Get total count
  const total = await collection.countDocuments(query);

  // Build sort
  const sortField = options.sortBy || 'createdAt';
  const sortOrder = options.sortOrder === 'asc' ? 1 : -1;

  // Get customers
  const customers = await collection
    .find(query)
    .sort({ [sortField]: sortOrder })
    .limit(options.limit || 50)
    .skip(options.offset || 0)
    .toArray();

  return { customers, total };
}

/**
 * Get customer with all related data
 */
export async function getCustomerWithRelations(id: string): Promise<CustomerWithRelations | null> {
  const customer = await getCustomerById(id);
  if (!customer) {
    return null;
  }

  const [interactions, notes, quotes] = await Promise.all([
    getCustomerInteractions(id),
    getCustomerNotes(id),
    getCustomerQuotes(id),
  ]);

  // Build recent activity timeline
  const recentActivity: CustomerWithRelations['recentActivity'] = [];

  interactions.forEach((int) => {
    recentActivity.push({
      type: 'interaction',
      date: int.occurredAt,
      description: `${int.type}: ${int.subject || int.content.substring(0, 50)}`,
    });
  });

  notes.forEach((note) => {
    recentActivity.push({
      type: 'note',
      date: note.createdAt,
      description: note.content.substring(0, 50),
    });
  });

  quotes.forEach((quote) => {
    recentActivity.push({
      type: 'quote',
      date: quote.createdAt,
      description: `Quote ${quote.quoteNumber} - $${quote.total.toFixed(2)}`,
    });
  });

  // Sort by date descending
  recentActivity.sort((a, b) => b.date.getTime() - a.date.getTime());

  return {
    ...customer,
    interactions,
    notes,
    quotes,
    recentActivity: recentActivity.slice(0, 20), // Last 20 activities
  };
}

/**
 * Update customer statistics
 */
export async function updateCustomerStats(id: string): Promise<void> {
  const { customers, quotes } = await getCollections();

  const customerQuotes = await quotes.find({ customerId: id }).toArray();

  const totalQuotes = customerQuotes.length;
  const totalRevenue = customerQuotes.reduce((sum, q) => sum + q.total, 0);

  await customers.updateOne(
    { _id: new ObjectId(id) },
    {
      $set: {
        'stats.totalQuotes': totalQuotes,
        'stats.totalRevenue': totalRevenue,
        'stats.lastContactDate': new Date(),
        updatedAt: new Date(),
      },
    }
  );
}

// ============================================================================
// INTERACTION OPERATIONS
// ============================================================================

/**
 * Create interaction
 */
export async function createInteraction(input: CreateInteractionInput): Promise<Interaction> {
  const { interactions } = await getCollections();

  const interaction: Interaction = {
    customerId: input.customerId,
    type: input.type,
    direction: input.direction,
    subject: input.subject,
    content: input.content,
    tags: input.tags || [],
    quoteId: input.quoteId,
    orderId: input.orderId,
    occurredAt: input.occurredAt || new Date(),
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const result = await interactions.insertOne(interaction);
  interaction._id = result.insertedId;

  // Update customer last contact date
  await updateCustomerStats(input.customerId);

  return interaction;
}

/**
 * Get customer interactions
 */
export async function getCustomerInteractions(
  customerId: string,
  limit = 100
): Promise<Interaction[]> {
  const { interactions } = await getCollections();

  return await interactions
    .find({ customerId })
    .sort({ occurredAt: -1 })
    .limit(limit)
    .toArray();
}

/**
 * Delete interaction
 */
export async function deleteInteraction(id: string): Promise<boolean> {
  const { interactions } = await getCollections();
  const result = await interactions.deleteOne({ _id: new ObjectId(id) });
  return result.deletedCount > 0;
}

// ============================================================================
// NOTE OPERATIONS
// ============================================================================

/**
 * Create note
 */
export async function createNote(input: CreateNoteInput): Promise<Note> {
  const { notes } = await getCollections();

  const note: Note = {
    customerId: input.customerId,
    content: input.content,
    isPinned: input.isPinned || false,
    tags: input.tags || [],
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const result = await notes.insertOne(note);
  note._id = result.insertedId;

  return note;
}

/**
 * Get customer notes
 */
export async function getCustomerNotes(customerId: string): Promise<Note[]> {
  const { notes } = await getCollections();

  return await notes
    .find({ customerId })
    .sort({ isPinned: -1, createdAt: -1 })
    .toArray();
}

/**
 * Update note
 */
export async function updateNote(
  id: string,
  updates: { content?: string; isPinned?: boolean; tags?: string[] }
): Promise<Note | null> {
  const { notes } = await getCollections();

  const result = await notes.findOneAndUpdate(
    { _id: new ObjectId(id) },
    {
      $set: {
        ...updates,
        updatedAt: new Date(),
      },
    },
    { returnDocument: 'after' }
  );

  return result || null;
}

/**
 * Delete note
 */
export async function deleteNote(id: string): Promise<boolean> {
  const { notes } = await getCollections();
  const result = await notes.deleteOne({ _id: new ObjectId(id) });
  return result.deletedCount > 0;
}

// ============================================================================
// QUOTE OPERATIONS
// ============================================================================

/**
 * Create quote
 */
export async function createQuote(quote: Omit<CRMQuote, '_id' | 'createdAt' | 'updatedAt'>): Promise<CRMQuote> {
  const { quotes } = await getCollections();

  const newQuote: CRMQuote = {
    ...quote,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const result = await quotes.insertOne(newQuote);
  newQuote._id = result.insertedId;

  // Update customer stats
  await updateCustomerStats(quote.customerId.toString());

  return newQuote;
}

/**
 * Get customer quotes
 */
export async function getCustomerQuotes(customerId: string): Promise<CRMQuote[]> {
  const { quotes } = await getCollections();

  return await quotes.find({ customerId }).sort({ createdAt: -1 }).toArray();
}

/**
 * Update quote status
 */
export async function updateQuoteStatus(
  quoteId: string,
  status: CRMQuote['status']
): Promise<CRMQuote | null> {
  const { quotes } = await getCollections();

  const result = await quotes.findOneAndUpdate(
    { _id: new ObjectId(quoteId) },
    {
      $set: {
        status,
        ...(status === 'accepted' ? { acceptedAt: new Date() } : {}),
        updatedAt: new Date(),
      },
    },
    { returnDocument: 'after' }
  );

  return result || null;
}

// ============================================================================
// CRM STATISTICS
// ============================================================================

/**
 * Get CRM statistics
 */
export async function getCRMStats(): Promise<CRMStats> {
  const { customers, interactions } = await getCollections();

  const [
    totalCustomers,
    customersByStatus,
    customersBySource,
    totalRevenueResult,
    recentInteractions,
  ] = await Promise.all([
    customers.countDocuments(),
    customers
      .aggregate([{ $group: { _id: '$status', count: { $sum: 1 } } }])
      .toArray(),
    customers
      .aggregate([{ $group: { _id: '$source', count: { $sum: 1 } } }])
      .toArray(),
    customers
      .aggregate([{ $group: { _id: null, total: { $sum: '$stats.totalRevenue' } } }])
      .toArray(),
    interactions.countDocuments(),
  ]);

  // Build status counts
  const statusCounts = { lead: 0, prospect: 0, customer: 0, inactive: 0 };
  customersByStatus.forEach((item: any) => {
    statusCounts[item._id as keyof typeof statusCounts] = item.count;
  });

  // Build source counts
  const sourceCounts = { quote: 0, mercadolibre: 0, manual: 0, import: 0 };
  customersBySource.forEach((item: any) => {
    sourceCounts[item._id as keyof typeof sourceCounts] = item.count;
  });

  // Get recent activity (last 30 days, grouped by day)
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

  const activityByDay = await interactions
    .aggregate([
      { $match: { createdAt: { $gte: thirtyDaysAgo } } },
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
          count: { $sum: 1 },
        },
      },
      { $sort: { _id: 1 } },
    ])
    .toArray();

  return {
    totalCustomers,
    totalInteractions: recentInteractions,
    totalRevenue: totalRevenueResult[0]?.total || 0,
    customersByStatus: statusCounts,
    customersBySource: sourceCounts,
    recentActivity: activityByDay.map((item: any) => ({
      date: item._id,
      count: item.count,
    })),
  };
}
