/**
 * Quote System → CRM Integration
 * Automatically create customers and log interactions from quotes
 */

import {
  getOrCreateCustomer,
  createInteraction,
  createQuote,
  updateCustomerStats,
  updateQuoteStatus,
  type CreateCustomerInput,
} from '../service';
import { sendQuoteEmail } from '@/lib/email';

export interface QuoteData {
  // Customer information
  customerEmail: string;
  customerName: string;
  customerPhone?: string;
  customerCompany?: string;

  // Quote details
  quoteNumber: string;
  items: Array<{
    name: string;
    quantity: number;
    unitPrice: number;
    total?: number;
  }>;
  subtotal: number;
  iva: number;
  total: number;
  validUntil?: string;

  // Optional metadata
  tags?: string[];
  notes?: string;
  source?: 'web' | 'email' | 'phone' | 'whatsapp';
}

/**
 * Process quote and create customer in CRM
 * This is the main integration function - use this when creating quotes
 */
export async function processQuoteWithCRM(quoteData: QuoteData): Promise<{
  customerId: string;
  quoteId: string;
  customer: any;
  emailSent: boolean;
}> {
  // 1. Get or create customer
  const customerInput: CreateCustomerInput = {
    email: quoteData.customerEmail,
    name: quoteData.customerName,
    phone: quoteData.customerPhone,
    company: quoteData.customerCompany,
    source: 'quote',
    status: 'lead', // New quote = lead
    tags: quoteData.tags || [],
  };

  const customer = await getOrCreateCustomer(customerInput);
  const customerId = customer._id!.toString();

  // 2. Create quote in CRM
  const quote = await createQuote({
    customerId: customer._id!,
    quoteNumber: quoteData.quoteNumber,
    items: quoteData.items.map((item) => ({
      name: item.name,
      quantity: item.quantity,
      unitPrice: item.unitPrice,
      total: item.total || item.quantity * item.unitPrice,
    })),
    subtotal: quoteData.subtotal,
    iva: quoteData.iva,
    total: quoteData.total,
    status: 'draft',
    validUntil: quoteData.validUntil ? new Date(quoteData.validUntil) : undefined,
  });

  const quoteId = quote._id!.toString();

  // 3. Log quote request interaction
  await createInteraction({
    customerId,
    type: quoteData.source === 'email' ? 'email' : 'other',
    direction: 'inbound',
    subject: `Quote Request #${quoteData.quoteNumber}`,
    content: `Customer requested quote for ${quoteData.items.length} items. Total: $${quoteData.total.toFixed(2)}${quoteData.notes ? `. Notes: ${quoteData.notes}` : ''}`,
    tags: ['quote-request', ...(quoteData.tags || [])],
    quoteId: quoteData.quoteNumber,
  });

  // 4. Send quote email (optional)
  let emailSent = false;
  try {
    await sendQuoteEmail(quoteData.customerEmail, {
      customerName: quoteData.customerName,
      quoteNumber: quoteData.quoteNumber,
      items: quoteData.items.map((item) => ({
        ...item,
        total: item.total || item.quantity * item.unitPrice,
      })),
      subtotal: quoteData.subtotal,
      iva: quoteData.iva,
      total: quoteData.total,
      validUntil: quoteData.validUntil,
    });

    // Log email sent interaction
    await createInteraction({
      customerId,
      type: 'email',
      direction: 'outbound',
      subject: `Quote Sent #${quoteData.quoteNumber}`,
      content: `Sent quote confirmation email with pricing details`,
      tags: ['automated', 'quote-sent'],
      quoteId: quoteData.quoteNumber,
    });

    // Update quote status
    await updateQuoteStatus(quoteId, 'sent');

    emailSent = true;
  } catch (error) {
    console.error('Failed to send quote email:', error);
    // Don't fail the quote creation if email fails
  }

  return {
    customerId,
    quoteId,
    customer,
    emailSent,
  };
}

/**
 * Log quote acceptance
 * Call this when customer accepts a quote
 */
export async function logQuoteAcceptance(
  customerId: string,
  quoteId: string,
  quoteNumber: string,
  orderAmount: number
): Promise<void> {
  // Update customer status to customer (they purchased!)
  const { updateCustomer } = await import('../service');
  await updateCustomer(customerId, {
    status: 'customer',
  });

  // Update quote status
  await updateQuoteStatus(quoteId, 'accepted');

  // Log acceptance interaction
  await createInteraction({
    customerId,
    type: 'other',
    direction: 'inbound',
    subject: `Quote Accepted #${quoteNumber}`,
    content: `Customer accepted quote and placed order. Amount: $${orderAmount.toFixed(2)}`,
    tags: ['quote-accepted', 'conversion'],
    quoteId: quoteNumber,
  });

  // Update customer stats
  await updateCustomerStats(customerId);
}

/**
 * Log quote rejection
 * Call this when customer rejects a quote
 */
export async function logQuoteRejection(
  customerId: string,
  quoteId: string,
  quoteNumber: string,
  reason?: string
): Promise<void> {
  // Update quote status
  await updateQuoteStatus(quoteId, 'rejected');

  // Log rejection interaction
  await createInteraction({
    customerId,
    type: 'other',
    direction: 'inbound',
    subject: `Quote Rejected #${quoteNumber}`,
    content: `Customer rejected quote${reason ? `. Reason: ${reason}` : ''}`,
    tags: ['quote-rejected'],
    quoteId: quoteNumber,
  });
}

/**
 * Log follow-up communication
 * Call this when you follow up on a quote
 */
export async function logQuoteFollowUp(
  customerId: string,
  quoteNumber: string,
  method: 'email' | 'call' | 'whatsapp',
  notes: string
): Promise<void> {
  await createInteraction({
    customerId,
    type: method,
    direction: 'outbound',
    subject: `Follow-up: Quote #${quoteNumber}`,
    content: notes,
    tags: ['follow-up', 'quote'],
    quoteId: quoteNumber,
  });
}

/**
 * Promote lead to prospect
 * Call this when customer shows interest but hasn't purchased yet
 */
export async function promoteToProspect(customerId: string, reason: string): Promise<void> {
  const { updateCustomer } = await import('../service');

  await updateCustomer(customerId, {
    status: 'prospect',
  });

  await createInteraction({
    customerId,
    type: 'note',
    subject: 'Promoted to Prospect',
    content: reason,
    tags: ['status-change', 'prospect'],
  });
}

/**
 * Batch process multiple quotes
 * Useful for importing historical quotes
 */
export async function batchProcessQuotes(
  quotes: QuoteData[],
  options: {
    sendEmails?: boolean;
    delayMs?: number;
    onProgress?: (processed: number, total: number) => void;
  } = {}
): Promise<{ processed: number; failed: number; errors: string[] }> {
  const { sendEmails = false, delayMs = 1000, onProgress } = options;
  const results = {
    processed: 0,
    failed: 0,
    errors: [] as string[],
  };

  for (let i = 0; i < quotes.length; i++) {
    try {
      await processQuoteWithCRM(quotes[i]);
      results.processed++;

      onProgress?.(i + 1, quotes.length);

      // Rate limiting
      if (i < quotes.length - 1 && delayMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    } catch (error) {
      results.failed++;
      results.errors.push(
        `Quote ${quotes[i].quoteNumber}: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
      console.error(`Failed to process quote ${quotes[i].quoteNumber}:`, error);
    }
  }

  return results;
}
