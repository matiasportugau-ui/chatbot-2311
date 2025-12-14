/**
 * Example: Integrating Email with Quote System
 *
 * This example shows how to automatically send email confirmations
 * when quotes are created in your system.
 */

import { sendQuoteEmail } from '@/lib/email';

/**
 * Example 1: Send email after creating a quote
 */
export async function createQuoteWithEmail(quoteData: {
  customerName: string;
  customerEmail: string;
  items: Array<{
    name: string;
    quantity: number;
    unitPrice: number;
  }>;
}) {
  // 1. Calculate totals
  const subtotal = quoteData.items.reduce(
    (sum, item) => sum + item.quantity * item.unitPrice,
    0
  );
  const iva = subtotal * 0.22; // 22% IVA for Uruguay
  const total = subtotal + iva;

  // 2. Generate quote number (example)
  const quoteNumber = `Q-${Date.now()}`;

  // 3. Save quote to database (your existing logic)
  // const savedQuote = await saveQuoteToDB({ ... });

  // 4. Send confirmation email
  try {
    await sendQuoteEmail(quoteData.customerEmail, {
      customerName: quoteData.customerName,
      quoteNumber,
      items: quoteData.items.map((item) => ({
        name: item.name,
        quantity: item.quantity,
        unitPrice: item.unitPrice,
        total: item.quantity * item.unitPrice,
      })),
      subtotal,
      iva,
      total,
      validUntil: getValidUntilDate(30), // Valid for 30 days
    });

    console.log(`✅ Quote email sent to ${quoteData.customerEmail}`);
  } catch (error) {
    console.error('❌ Failed to send quote email:', error);
    // Don't fail the quote creation if email fails
    // Just log the error and continue
  }

  return {
    quoteNumber,
    subtotal,
    iva,
    total,
    emailSent: true,
  };
}

/**
 * Example 2: Send quote via API endpoint
 */
export async function sendQuoteViaAPI(quoteId: string, customerEmail: string) {
  // Fetch quote from database
  // const quote = await getQuoteFromDB(quoteId);

  // Example quote data
  const quote = {
    id: 'Q-12345',
    customerName: 'Juan Pérez',
    items: [
      {
        name: 'Panel Isodec 100mm',
        quantity: 10,
        unitPrice: 150.0,
        total: 1500.0,
      },
      {
        name: 'Chapa Trapezoidal',
        quantity: 5,
        unitPrice: 200.0,
        total: 1000.0,
      },
    ],
    subtotal: 2500.0,
    iva: 550.0,
    total: 3050.0,
  };

  // Send email via API
  const response = await fetch('http://localhost:3000/api/email/quote', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      to: customerEmail,
      data: {
        customerName: quote.customerName,
        quoteNumber: quote.id,
        items: quote.items,
        subtotal: quote.subtotal,
        iva: quote.iva,
        total: quote.total,
        validUntil: getValidUntilDate(30),
      },
    }),
  });

  const result = await response.json();
  return result;
}

/**
 * Example 3: Batch send quotes to multiple customers
 */
export async function sendQuotesToMultipleCustomers(
  quotes: Array<{
    customerEmail: string;
    customerName: string;
    quoteNumber: string;
    items: any[];
    subtotal: number;
    iva: number;
    total: number;
  }>
) {
  const results = {
    sent: 0,
    failed: 0,
    errors: [] as string[],
  };

  for (const quote of quotes) {
    try {
      await sendQuoteEmail(quote.customerEmail, {
        customerName: quote.customerName,
        quoteNumber: quote.quoteNumber,
        items: quote.items,
        subtotal: quote.subtotal,
        iva: quote.iva,
        total: quote.total,
      });

      results.sent++;
      console.log(`✅ Sent quote to ${quote.customerEmail}`);

      // Rate limiting: Wait 1 second between emails
      await new Promise((resolve) => setTimeout(resolve, 1000));
    } catch (error) {
      results.failed++;
      results.errors.push(
        `${quote.customerEmail}: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
      console.error(`❌ Failed to send quote to ${quote.customerEmail}:`, error);
    }
  }

  return results;
}

/**
 * Example 4: Send quote reminder for expiring quotes
 */
export async function sendQuoteExpirationReminder(
  customerEmail: string,
  quoteNumber: string,
  daysUntilExpiration: number
) {
  const { sendCustomEmail } = await import('@/lib/email');

  await sendCustomEmail({
    to: customerEmail,
    subject: `Reminder: Quote ${quoteNumber} expires in ${daysUntilExpiration} days`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #f59e0b;">Quote Expiring Soon</h1>
        <p>Dear Customer,</p>
        <p>This is a friendly reminder that your quote <strong>${quoteNumber}</strong> will expire in <strong>${daysUntilExpiration} days</strong>.</p>
        <p>If you'd like to proceed with this quote, please let us know before it expires.</p>
        <div style="margin: 30px 0; padding: 20px; background-color: #fef3c7; border-left: 4px solid #f59e0b;">
          <p style="margin: 0; font-weight: bold;">Don't miss out!</p>
          <p style="margin: 5px 0 0 0;">Reply to this email or contact us to confirm your order.</p>
        </div>
        <p>Best regards,<br>BMC Team</p>
      </div>
    `,
    text: `
Quote Expiring Soon

Dear Customer,

This is a friendly reminder that your quote ${quoteNumber} will expire in ${daysUntilExpiration} days.

If you'd like to proceed with this quote, please let us know before it expires.

Don't miss out! Reply to this email or contact us to confirm your order.

Best regards,
BMC Team
    `.trim(),
  });
}

/**
 * Helper: Get valid until date (X days from now)
 */
function getValidUntilDate(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toLocaleDateString('es-UY', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Example 5: Integration with API route
 *
 * In your quote creation API route:
 *
 * // src/app/api/quotes/create/route.ts
 * import { sendQuoteEmail } from '@/lib/email';
 *
 * export async function POST(request: Request) {
 *   const body = await request.json();
 *
 *   // Create quote in database
 *   const quote = await createQuote(body);
 *
 *   // Send email confirmation (don't await - send in background)
 *   sendQuoteEmail(body.customerEmail, {
 *     customerName: body.customerName,
 *     quoteNumber: quote.id,
 *     items: quote.items,
 *     subtotal: quote.subtotal,
 *     iva: quote.iva,
 *     total: quote.total,
 *   }).catch(error => {
 *     console.error('Failed to send quote email:', error);
 *   });
 *
 *   return NextResponse.json({ success: true, quote });
 * }
 */
