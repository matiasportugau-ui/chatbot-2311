# Email Integration Examples

This directory contains comprehensive examples showing how to integrate the email automation system with your existing workflows.

## 📁 Files Overview

### 1. [email-integration-quote.ts](email-integration-quote.ts)
**Quote System Email Integration**

Examples for automatically sending quote confirmations to customers.

**Includes:**
- ✅ Send email after creating a quote
- ✅ Send quote via API endpoint
- ✅ Batch send quotes to multiple customers
- ✅ Send quote expiration reminders
- ✅ Integration with API routes

**Use Cases:**
- Automated quote confirmations
- Follow-up emails for expiring quotes
- Bulk quote distribution

---

### 2. [email-integration-mercadolibre.ts](email-integration-mercadolibre.ts)
**Mercado Libre Order Email Integration**

Examples for automatically sending order notifications when Mercado Libre orders are received.

**Includes:**
- ✅ Send order confirmation via webhook
- ✅ Send emails after manual order sync
- ✅ Send shipping notifications with tracking
- ✅ Send delivery confirmations
- ✅ Integration with webhook handler

**Use Cases:**
- Order confirmations for Mercado Libre sales
- Shipping status updates
- Delivery notifications
- Customer review requests

---

### 3. [email-automation-utils.ts](email-automation-utils.ts)
**Email Automation Utilities**

Helper classes and functions for common email automation tasks.

**Includes:**
- ✅ **EmailQueue** - Rate-limited email queue manager
- ✅ **sendEmailWithRetry** - Automatic retry with exponential backoff
- ✅ **EmailTemplateBuilder** - Simplified HTML email builder
- ✅ **EmailScheduler** - Schedule emails for future delivery
- ✅ **sendBulkEmails** - Bulk sending with progress tracking

**Use Cases:**
- Rate limiting to avoid spam filters
- Reliable email delivery with retries
- Quick HTML email creation
- Scheduled reminders and follow-ups
- Newsletter/bulk email campaigns

---

## 🚀 Quick Start

### 1. Quote Email Integration

```typescript
import { createQuoteWithEmail } from './examples/email-integration-quote';

// Create quote and send confirmation email
const result = await createQuoteWithEmail({
  customerName: 'Juan Pérez',
  customerEmail: 'juan@example.com',
  items: [
    {
      name: 'Panel Isodec 100mm',
      quantity: 10,
      unitPrice: 150.00
    }
  ]
});

console.log(`Quote ${result.quoteNumber} created and email sent!`);
```

### 2. Mercado Libre Order Email

```typescript
import { handleMercadoLibreOrderCreated } from './examples/email-integration-mercadolibre';

// In your webhook handler
export async function POST(request: Request) {
  const notification = await request.json();

  if (notification.topic === 'orders_v2') {
    const order = await fetchOrderFromMercadoLibre(notification.resource);

    // Send order confirmation email automatically
    await handleMercadoLibreOrderCreated(order);
  }

  return new Response('OK', { status: 200 });
}
```

### 3. Using Email Utilities

```typescript
import { EmailQueue, EmailTemplateBuilder } from './examples/email-automation-utils';

// Create rate-limited email queue
const queue = new EmailQueue(1000); // 1 second between emails

// Add emails to queue
queue.add(() => sendQuoteEmail(email1, data1));
queue.add(() => sendQuoteEmail(email2, data2));
queue.add(() => sendOrderEmail(email3, data3));

// Build custom email template
const html = new EmailTemplateBuilder()
  .header('Welcome!', 'Thanks for joining BMC')
  .paragraph('We\'re excited to have you.')
  .callout('Check out our latest products!', 'info')
  .button('Browse Catalog', 'https://example.com/catalog')
  .footer('Best regards,<br>BMC Team')
  .build();

await sendCustomEmail({
  to: 'customer@example.com',
  subject: 'Welcome to BMC!',
  html
});
```

---

## 📋 Common Integration Patterns

### Pattern 1: Fire-and-Forget Email

Send email without blocking the main operation:

```typescript
// In your API route
export async function POST(request: Request) {
  const quote = await createQuote(requestData);

  // Send email in background (don't await)
  sendQuoteEmail(quote.customerEmail, quoteData)
    .catch(error => console.error('Email failed:', error));

  // Return immediately
  return NextResponse.json({ success: true, quote });
}
```

### Pattern 2: Email with Retry Logic

Ensure emails are delivered even if first attempt fails:

```typescript
import { sendEmailWithRetry } from './examples/email-automation-utils';

await sendEmailWithRetry(
  () => sendQuoteEmail(customerEmail, quoteData),
  3,     // max retries
  1000   // initial delay (ms)
);
```

### Pattern 3: Batch Email Processing

Send multiple emails with rate limiting:

```typescript
import { EmailQueue } from './examples/email-automation-utils';

const queue = new EmailQueue(1000); // 1 second delay

customers.forEach(customer => {
  queue.add(() => sendQuoteEmail(customer.email, customer.quoteData));
});

// Check queue status
console.log(queue.getStatus());
// { pending: 5, processing: true }
```

### Pattern 4: Scheduled Email Reminders

Schedule emails for future delivery:

```typescript
import { EmailScheduler } from './examples/email-automation-utils';

const scheduler = new EmailScheduler();

// Schedule quote reminder for 7 days from now
const reminderDate = new Date();
reminderDate.setDate(reminderDate.getDate() + 7);

scheduler.schedule(
  `quote-reminder-${quoteId}`,
  reminderDate,
  () => sendQuoteExpirationReminder(email, quoteId, 7)
);

// Cancel if customer confirms order early
scheduler.cancel(`quote-reminder-${quoteId}`);
```

### Pattern 5: Progress Tracking for Bulk Emails

Send bulk emails with progress updates:

```typescript
import { sendBulkEmails } from './examples/email-automation-utils';

const results = await sendBulkEmails(
  emailList,
  {
    delayMs: 1000,
    onProgress: (sent, total) => {
      console.log(`Progress: ${sent}/${total} (${Math.round(sent/total*100)}%)`);
    },
    onError: (email, error) => {
      console.error(`Failed to send to ${email}:`, error.message);
    }
  }
);

console.log(`Success: ${results.sent}, Failed: ${results.failed}`);
```

---

## 🎯 Integration Checklist

### Quote System Integration

- [ ] Import email functions into quote creation module
- [ ] Add email sending after quote is saved to database
- [ ] Handle email errors gracefully (don't fail quote creation)
- [ ] Add quote expiration reminder scheduler
- [ ] Test with real customer email

### Mercado Libre Integration

- [ ] Add email sending to webhook handler
- [ ] Handle order status changes (paid, shipped, delivered)
- [ ] Format Mercado Libre data for email templates
- [ ] Test with sandbox Mercado Libre orders
- [ ] Monitor webhook logs for email errors

### General Email Automation

- [ ] Set up email queue for rate limiting
- [ ] Implement retry logic for critical emails
- [ ] Create custom email templates for your business
- [ ] Set up email monitoring/logging
- [ ] Test bulk email sending limits (Gmail: ~500/day)

---

## ⚠️ Important Notes

### Rate Limiting

Gmail free tier has sending limits:
- **~500 emails per day** for free Gmail accounts
- **~2000 emails per day** for Google Workspace accounts

**Best Practices:**
- Use EmailQueue with 1-2 second delays between emails
- Don't send more than 100 emails per hour
- Monitor for bounce/spam reports

### Error Handling

**Always handle email errors gracefully:**

```typescript
try {
  await sendQuoteEmail(email, data);
} catch (error) {
  console.error('Email failed:', error);
  // Log to monitoring system
  // Don't fail the main operation
}
```

### Testing

**Test emails before production:**

1. **Development**: Use your own email address
2. **Staging**: Test with team emails
3. **Production**: Start with small batches

**Check for:**
- ✅ Correct formatting on mobile devices
- ✅ Links work correctly
- ✅ Images load (if any)
- ✅ Emails don't go to spam
- ✅ Unsubscribe links work (for newsletters)

### Email Deliverability

**Improve deliverability:**

1. **Use a consistent "From" name**
   - Set `SMTP_FROM_NAME=BMC Chatbot` in `.env`

2. **Avoid spam triggers**
   - Don't use all caps in subject lines
   - Avoid excessive exclamation marks
   - Include unsubscribe link for bulk emails
   - Maintain text/HTML ratio

3. **Monitor bounces**
   - Remove invalid emails from your list
   - Check Gmail "Sent" folder for delivery status

4. **Consider upgrading**
   - For production, consider SendGrid/Mailgun
   - Better deliverability and analytics
   - Higher sending limits

---

## 🔗 Related Documentation

- [EMAIL_SETUP.md](../EMAIL_SETUP.md) - Email service setup guide
- [MERCADOLIBRE_SETUP.md](../MERCADOLIBRE_SETUP.md) - Mercado Libre integration guide
- [Nodemailer Documentation](https://nodemailer.com/) - Official Nodemailer docs
- [Gmail Sending Limits](https://support.google.com/a/answer/166852) - Google's official limits

---

## 💡 Tips & Tricks

### Tip 1: Debug Email Content

View generated HTML in browser:

```typescript
import { generateQuoteEmail } from '@/lib/email/templates';
import fs from 'fs';

const html = generateQuoteEmail(quoteData);
fs.writeFileSync('email-preview.html', html);
// Open email-preview.html in browser
```

### Tip 2: Email Analytics

Track email opens and clicks:

```typescript
// Add tracking pixel to email HTML
const trackingPixel = `<img src="https://yourdomain.com/api/email/track/${emailId}/open.gif" width="1" height="1" />`;

// Add UTM parameters to links
const trackedLink = `https://example.com/quote?utm_source=email&utm_campaign=quote_${quoteId}`;
```

### Tip 3: Email Templates in Database

Store templates in MongoDB for easy editing:

```typescript
// Save template
await db.collection('email_templates').insertOne({
  name: 'quote_confirmation',
  subject: 'Your Quote #{{quoteNumber}}',
  html: '<h1>Quote {{quoteNumber}}</h1>...',
  variables: ['quoteNumber', 'customerName', 'total']
});

// Load and render template
const template = await db.collection('email_templates').findOne({ name: 'quote_confirmation' });
const html = renderTemplate(template.html, { quoteNumber, customerName, total });
```

---

## 🐛 Troubleshooting

### Emails not sending

1. Check email configuration: `curl http://localhost:3000/api/email/test`
2. Verify SMTP credentials in `.env`
3. Check Gmail "Less secure apps" settings (should be OFF, use App Password instead)
4. Check server logs for error messages

### Emails going to spam

1. Add sender to recipient's contacts
2. Ask recipients to mark as "Not Spam"
3. Improve email content (avoid spam trigger words)
4. Consider using verified domain email (SendGrid/Mailgun)

### Rate limit exceeded

1. Reduce sending frequency (increase delay in EmailQueue)
2. Spread emails over multiple days
3. Upgrade to Google Workspace or dedicated email service

---

## 📞 Support

For issues or questions:
- Check [EMAIL_SETUP.md](../EMAIL_SETUP.md) troubleshooting section
- Review [Nodemailer documentation](https://nodemailer.com/about/)
- Contact your development team
