/**
 * Email Automation Utilities
 *
 * Helper functions and patterns for common email automation tasks.
 */

import { sendCustomEmail } from '@/lib/email';

/**
 * Email Queue Manager
 * Handles rate limiting and batch email sending
 */
export class EmailQueue {
  private queue: Array<() => Promise<void>> = [];
  private processing = false;
  private delayMs: number;

  constructor(delayMs = 1000) {
    this.delayMs = delayMs;
  }

  /**
   * Add email to queue
   */
  add(emailFn: () => Promise<void>) {
    this.queue.push(emailFn);
    this.process();
  }

  /**
   * Process queue with rate limiting
   */
  private async process() {
    if (this.processing) return;

    this.processing = true;

    while (this.queue.length > 0) {
      const emailFn = this.queue.shift();
      if (emailFn) {
        try {
          await emailFn();
          console.log(`✅ Email sent (${this.queue.length} remaining)`);
        } catch (error) {
          console.error('❌ Email failed:', error);
        }

        // Rate limiting delay
        if (this.queue.length > 0) {
          await new Promise((resolve) => setTimeout(resolve, this.delayMs));
        }
      }
    }

    this.processing = false;
  }

  /**
   * Get queue status
   */
  getStatus() {
    return {
      pending: this.queue.length,
      processing: this.processing,
    };
  }
}

/**
 * Usage example:
 *
 * const emailQueue = new EmailQueue(1000); // 1 second delay between emails
 *
 * emailQueue.add(() => sendQuoteEmail('customer1@example.com', quoteData1));
 * emailQueue.add(() => sendQuoteEmail('customer2@example.com', quoteData2));
 * emailQueue.add(() => sendOrderEmail('customer3@example.com', orderData3));
 */

/**
 * Email Retry Utility
 * Automatically retry failed emails with exponential backoff
 */
export async function sendEmailWithRetry<T extends (...args: any[]) => Promise<void>>(
  emailFn: T,
  maxRetries = 3,
  initialDelayMs = 1000
): Promise<void> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await emailFn();
      return; // Success!
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      console.error(`❌ Email attempt ${attempt + 1} failed:`, lastError.message);

      if (attempt < maxRetries - 1) {
        // Exponential backoff: 1s, 2s, 4s, etc.
        const delayMs = initialDelayMs * Math.pow(2, attempt);
        console.log(`⏳ Retrying in ${delayMs}ms...`);
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
  }

  throw new Error(`Failed after ${maxRetries} attempts: ${lastError?.message}`);
}

/**
 * Usage example:
 *
 * await sendEmailWithRetry(
 *   () => sendQuoteEmail(customerEmail, quoteData),
 *   3, // max retries
 *   1000 // initial delay
 * );
 */

/**
 * Email Template Builder
 * Simplified HTML email builder with common components
 */
export class EmailTemplateBuilder {
  private parts: string[] = [];

  header(title: string, subtitle?: string) {
    this.parts.push(`
      <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h1 style="color: #1f2937; margin: 0 0 ${subtitle ? '10px' : '0'} 0;">${title}</h1>
        ${subtitle ? `<p style="color: #6b7280; margin: 0;">${subtitle}</p>` : ''}
      </div>
    `);
    return this;
  }

  paragraph(text: string) {
    this.parts.push(`<p>${text}</p>`);
    return this;
  }

  infoBox(title: string, items: Array<{ label: string; value: string }>) {
    const itemsHtml = items
      .map(
        (item) =>
          `<p style="margin: 5px 0;"><strong>${item.label}:</strong> ${item.value}</p>`
      )
      .join('');

    this.parts.push(`
      <div style="background-color: #f9fafb; padding: 15px; border-radius: 6px; margin: 20px 0;">
        ${title ? `<p style="margin: 0 0 10px 0; font-weight: bold;">${title}</p>` : ''}
        ${itemsHtml}
      </div>
    `);
    return this;
  }

  callout(message: string, type: 'info' | 'warning' | 'success' = 'info') {
    const colors = {
      info: { bg: '#eff6ff', border: '#3b82f6' },
      warning: { bg: '#fef3c7', border: '#f59e0b' },
      success: { bg: '#dcfce7', border: '#10b981' },
    };

    const color = colors[type];

    this.parts.push(`
      <div style="background-color: ${color.bg}; padding: 15px; border-left: 4px solid ${color.border}; margin: 20px 0;">
        <p style="margin: 0;">${message}</p>
      </div>
    `);
    return this;
  }

  button(text: string, url: string) {
    this.parts.push(`
      <div style="text-align: center; margin: 30px 0;">
        <a href="${url}" style="display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
          ${text}
        </a>
      </div>
    `);
    return this;
  }

  footer(text: string) {
    this.parts.push(`
      <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
        <p>${text}</p>
      </div>
    `);
    return this;
  }

  build(): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        ${this.parts.join('\n')}
      </body>
      </html>
    `;
  }
}

/**
 * Usage example:
 *
 * const html = new EmailTemplateBuilder()
 *   .header('Payment Received', 'Thank you for your payment')
 *   .paragraph('Dear Customer,')
 *   .paragraph('We have received your payment successfully.')
 *   .infoBox('Payment Details', [
 *     { label: 'Amount', value: '$3,050.00' },
 *     { label: 'Date', value: '2024-12-14' },
 *     { label: 'Method', value: 'Credit Card' }
 *   ])
 *   .callout('Your order will be shipped within 24 hours.', 'success')
 *   .button('Track Order', 'https://example.com/track/12345')
 *   .footer('Best regards,<br>BMC Team')
 *   .build();
 *
 * await sendCustomEmail({
 *   to: customerEmail,
 *   subject: 'Payment Received',
 *   html
 * });
 */

/**
 * Email Scheduler
 * Schedule emails to be sent at specific times
 */
export class EmailScheduler {
  private scheduled: Map<string, NodeJS.Timeout> = new Map();

  /**
   * Schedule an email to be sent at a specific time
   */
  schedule(
    id: string,
    sendAt: Date,
    emailFn: () => Promise<void>
  ): void {
    const now = Date.now();
    const sendAtMs = sendAt.getTime();
    const delayMs = sendAtMs - now;

    if (delayMs <= 0) {
      console.warn('Scheduled time is in the past, sending immediately');
      emailFn().catch(console.error);
      return;
    }

    // Cancel existing scheduled email with same ID
    this.cancel(id);

    // Schedule new email
    const timeout = setTimeout(() => {
      emailFn()
        .then(() => console.log(`✅ Scheduled email ${id} sent`))
        .catch((error) => console.error(`❌ Scheduled email ${id} failed:`, error))
        .finally(() => this.scheduled.delete(id));
    }, delayMs);

    this.scheduled.set(id, timeout);
    console.log(`📅 Email ${id} scheduled for ${sendAt.toLocaleString()}`);
  }

  /**
   * Cancel a scheduled email
   */
  cancel(id: string): boolean {
    const timeout = this.scheduled.get(id);
    if (timeout) {
      clearTimeout(timeout);
      this.scheduled.delete(id);
      console.log(`🚫 Cancelled scheduled email ${id}`);
      return true;
    }
    return false;
  }

  /**
   * Get list of scheduled emails
   */
  getScheduled(): string[] {
    return Array.from(this.scheduled.keys());
  }
}

/**
 * Usage example:
 *
 * const scheduler = new EmailScheduler();
 *
 * // Schedule quote reminder for 7 days from now
 * const reminderDate = new Date();
 * reminderDate.setDate(reminderDate.getDate() + 7);
 *
 * scheduler.schedule(
 *   `quote-reminder-${quoteId}`,
 *   reminderDate,
 *   () => sendQuoteExpirationReminder(customerEmail, quoteId, 7)
 * );
 *
 * // Cancel if needed
 * scheduler.cancel(`quote-reminder-${quoteId}`);
 */

/**
 * Bulk Email Sender with Progress Tracking
 */
export async function sendBulkEmails(
  emails: Array<{
    to: string;
    subject: string;
    html: string;
    text?: string;
  }>,
  options: {
    delayMs?: number;
    onProgress?: (sent: number, total: number) => void;
    onError?: (email: string, error: Error) => void;
  } = {}
): Promise<{ sent: number; failed: number }> {
  const { delayMs = 1000, onProgress, onError } = options;
  const results = { sent: 0, failed: 0 };

  for (let i = 0; i < emails.length; i++) {
    const email = emails[i];

    try {
      await sendCustomEmail(email);
      results.sent++;
      console.log(`✅ Sent ${i + 1}/${emails.length} to ${email.to}`);
    } catch (error) {
      results.failed++;
      const err = error instanceof Error ? error : new Error(String(error));
      console.error(`❌ Failed to send to ${email.to}:`, err.message);
      onError?.(email.to, err);
    }

    // Progress callback
    onProgress?.(i + 1, emails.length);

    // Rate limiting
    if (i < emails.length - 1) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }

  return results;
}

/**
 * Usage example:
 *
 * const results = await sendBulkEmails(
 *   [
 *     { to: 'customer1@example.com', subject: 'Newsletter', html: '<h1>News</h1>' },
 *     { to: 'customer2@example.com', subject: 'Newsletter', html: '<h1>News</h1>' }
 *   ],
 *   {
 *     delayMs: 1000,
 *     onProgress: (sent, total) => console.log(`Progress: ${sent}/${total}`),
 *     onError: (email, error) => console.error(`Failed: ${email}`)
 *   }
 * );
 *
 * console.log(`Sent: ${results.sent}, Failed: ${results.failed}`);
 */
