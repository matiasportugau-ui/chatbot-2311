# Email Automation Setup Guide

This guide will help you set up email automation for your BMC chatbot platform using Nodemailer with Gmail SMTP (completely free).

## Prerequisites

- A Gmail account
- Your application running on Next.js
- MongoDB database configured

## Step 1: Enable Gmail App Passwords

Since Gmail requires 2-factor authentication for app passwords, you'll need to set this up:

### 1.1 Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "How you sign in to Google", click on "2-Step Verification"
3. Follow the prompts to enable 2FA if not already enabled

### 1.2 Generate App Password

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Or: Google Account → Security → 2-Step Verification → App passwords
2. Click "Select app" → Choose "Mail"
3. Click "Select device" → Choose "Other (Custom name)"
4. Enter name: "BMC Chatbot" or similar
5. Click "Generate"
6. **Copy the 16-character password** (format: xxxx xxxx xxxx xxxx)
   - **IMPORTANT**: Save this password immediately - you won't be able to see it again!

## Step 2: Configure Environment Variables

Add the following variables to your `.env` file:

```bash
# Email Configuration (Gmail SMTP)
SMTP_USER=your.email@gmail.com
SMTP_APP_PASSWORD=your_16_char_app_password_here
SMTP_FROM_NAME=BMC Chatbot

# Optional: Advanced SMTP Configuration
# SMTP_HOST=smtp.gmail.com (default)
# SMTP_PORT=587 (default)
# SMTP_SECURE=false (default - use true for port 465)
```

### Example

```bash
SMTP_USER=matias@example.com
SMTP_APP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM_NAME=BMC Support Team
```

**Security Notes:**
- Never commit `.env` to git (already in `.gitignore`)
- Remove spaces from app password if pasting: `abcd efgh ijkl mnop` → `abcdefghijklmnop`
- Keep your app password secret

## Step 3: Verify Configuration

### 3.1 Check Configuration Status

```bash
curl http://localhost:3000/api/email/test
```

**Expected response** (configured):
```json
{
  "configured": true,
  "connected": true,
  "message": "Email service is configured and connected"
}
```

**Expected response** (not configured):
```json
{
  "configured": false,
  "message": "Email service not configured",
  "instructions": "Set SMTP_USER and SMTP_APP_PASSWORD environment variables"
}
```

### 3.2 Send Test Email

```bash
curl -X POST http://localhost:3000/api/email/test \
  -H "Content-Type: application/json" \
  -d '{"to": "your.email@example.com"}'
```

**Expected response**:
```json
{
  "success": true,
  "message": "Test email sent successfully to your.email@example.com"
}
```

**Check your inbox** - you should receive an email titled "BMC Email Service - Test Email"

## Step 4: API Endpoints Reference

### Check Configuration Status

**Endpoint**: `GET /api/email/test`

**Response**:
```json
{
  "configured": true,
  "connected": true,
  "message": "Email service is configured and connected"
}
```

---

### Send Test Email

**Endpoint**: `POST /api/email/test`

**Request Body**:
```json
{
  "to": "customer@example.com"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Test email sent successfully to customer@example.com"
}
```

---

### Send Quote Email

**Endpoint**: `POST /api/email/quote`

**Request Body**:
```json
{
  "to": "customer@example.com",
  "data": {
    "customerName": "John Doe",
    "quoteNumber": "Q-2024-001",
    "items": [
      {
        "name": "Panel Isodec 100mm",
        "quantity": 10,
        "unitPrice": 150.00,
        "total": 1500.00
      },
      {
        "name": "Chapa Trapezoidal",
        "quantity": 5,
        "unitPrice": 200.00,
        "total": 1000.00
      }
    ],
    "subtotal": 2500.00,
    "iva": 550.00,
    "total": 3050.00,
    "validUntil": "2024-12-31"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Quote email sent successfully to customer@example.com",
  "quoteNumber": "Q-2024-001"
}
```

---

### Send Order Email

**Endpoint**: `POST /api/email/order`

**Request Body**:
```json
{
  "to": "customer@example.com",
  "data": {
    "customerName": "Jane Smith",
    "orderNumber": "ORD-2024-001",
    "orderDate": "2024-12-14",
    "items": [
      {
        "name": "Panel Isodec 100mm",
        "quantity": 10,
        "price": 1500.00
      }
    ],
    "total": 1830.00,
    "shippingAddress": "Av. 18 de Julio 1234, Montevideo, Uruguay",
    "trackingNumber": "TRACK123456"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Order email sent successfully to customer@example.com",
  "orderNumber": "ORD-2024-001"
}
```

---

### Send Custom Email

**Endpoint**: `POST /api/email/send`

**Request Body**:
```json
{
  "to": "customer@example.com",
  "subject": "Your Custom Subject",
  "html": "<h1>Hello!</h1><p>This is a custom email.</p>",
  "text": "Hello! This is a custom email."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Email sent successfully to customer@example.com"
}
```

## Step 5: Integration Examples

### Example 1: Send Quote Email from Quote System

```typescript
// In your quote creation logic
import { sendQuoteEmail } from '@/lib/email';

async function createQuote(quoteData: any) {
  // ... create quote in database ...

  // Send confirmation email
  try {
    await sendQuoteEmail(quoteData.customerEmail, {
      customerName: quoteData.customerName,
      quoteNumber: quoteData.id,
      items: quoteData.items,
      subtotal: quoteData.subtotal,
      iva: quoteData.iva,
      total: quoteData.total,
      validUntil: quoteData.validUntil,
    });
  } catch (error) {
    console.error('Failed to send quote email:', error);
    // Don't fail the quote creation if email fails
  }
}
```

### Example 2: Send Order Email from Mercado Libre Integration

```typescript
// In your Mercado Libre order webhook handler
import { sendOrderEmail } from '@/lib/email';

async function handleNewOrder(orderData: any) {
  // ... process order ...

  // Send confirmation email
  await sendOrderEmail(orderData.buyer.email, {
    customerName: orderData.buyer.nickname,
    orderNumber: orderData.id.toString(),
    orderDate: new Date(orderData.date_created).toLocaleDateString(),
    items: orderData.order_items.map((item: any) => ({
      name: item.item.title,
      quantity: item.quantity,
      price: item.unit_price * item.quantity,
    })),
    total: orderData.total_amount,
    shippingAddress: formatAddress(orderData.shipping),
  });
}
```

## Troubleshooting

### Error: "Authentication failed"

**Possible causes:**
1. Incorrect email or app password
2. App password has spaces (remove them)
3. 2FA not enabled on Gmail account

**Solution:**
- Verify `SMTP_USER` is your full Gmail address
- Regenerate app password and update `.env`
- Ensure 2FA is enabled on your Google account

---

### Error: "Email service not configured"

**Solution:**
- Ensure both `SMTP_USER` and `SMTP_APP_PASSWORD` are set in `.env`
- Restart your Next.js server after updating `.env`

---

### Error: "Connection timeout"

**Possible causes:**
1. Firewall blocking port 587
2. ISP blocking SMTP

**Solution:**
- Try using port 465 with `SMTP_PORT=465` and `SMTP_SECURE=true`
- Check firewall settings
- Contact your hosting provider

---

### Emails going to spam

**Solutions:**
- Use a verified domain email instead of Gmail
- Add SPF and DKIM records if using custom domain
- Ask recipients to whitelist your sender email

---

### "App password not available"

**Solution:**
- Ensure 2FA is enabled on your Google account
- Use a Google Workspace account (not all Gmail accounts support app passwords)

## Email Templates

The email service includes professionally designed HTML email templates:

### Quote Email Template
- Clean, modern design
- Itemized product list with pricing
- Subtotal, IVA, and total breakdown
- Valid until date (optional)
- Call-to-action for next steps

### Order Email Template
- Order confirmation header
- Order details (number, date)
- Shipping address and tracking (optional)
- Itemized order list
- Total amount
- What happens next section

### Custom Templates

You can create custom email templates by using the `sendCustomEmail` function:

```typescript
import { sendCustomEmail } from '@/lib/email';

await sendCustomEmail({
  to: 'customer@example.com',
  subject: 'Payment Reminder',
  html: `
    <div style="font-family: Arial; padding: 20px;">
      <h1>Payment Reminder</h1>
      <p>Dear Customer,</p>
      <p>This is a friendly reminder about your pending payment.</p>
    </div>
  `,
  text: 'Payment Reminder\n\nDear Customer,\n\nThis is a friendly reminder about your pending payment.'
});
```

## Security Best Practices

1. **Never commit credentials**
   - `.env` is already in `.gitignore`
   - Use environment variables in production

2. **Rotate app passwords periodically**
   - Change every 6-12 months
   - Revoke old passwords after rotation

3. **Use HTTPS in production**
   - Protects email content in transit
   - Required for production deployments

4. **Rate limiting** (optional)
   - Implement rate limiting to prevent abuse
   - Gmail has sending limits (~500 emails/day for free accounts)

5. **Email validation**
   - Validate email addresses before sending
   - Handle bounces and invalid addresses

## Production Deployment

### Environment Variables on Vercel/Railway

1. Go to your project settings
2. Add environment variables:
   ```
   SMTP_USER=your.email@gmail.com
   SMTP_APP_PASSWORD=your_app_password
   SMTP_FROM_NAME=BMC Chatbot
   ```
3. Redeploy your application

### Using Custom Domain Email

For production, consider using:
- **SendGrid** (free tier: 100 emails/day)
- **Mailgun** (free tier: 5,000 emails/month)
- **Custom SMTP** with your domain

Update `.env`:
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_APP_PASSWORD=your_sendgrid_api_key
SMTP_FROM_NAME=BMC Support
```

## Testing Checklist

- [ ] Gmail 2FA enabled
- [ ] App password generated
- [ ] Environment variables configured
- [ ] Configuration status checked (`GET /api/email/test`)
- [ ] Test email sent successfully (`POST /api/email/test`)
- [ ] Test email received in inbox
- [ ] Quote email template tested
- [ ] Order email template tested
- [ ] Custom email tested
- [ ] Integration with quote system working
- [ ] Integration with order system working

## Next Steps

After email automation is working:

1. **Integrate with quote system**
   - Automatically send quote confirmations
   - Send quote expiration reminders

2. **Integrate with order system**
   - Send order confirmations
   - Send shipping notifications
   - Send delivery confirmations

3. **Set up email notifications**
   - Low stock alerts
   - Payment received
   - Customer support requests

4. **Monitor email delivery**
   - Track sent emails in database
   - Log delivery failures
   - Set up alerts for issues

## Support

For issues with:
- **Gmail App Passwords**: [Google Support](https://support.google.com/accounts/answer/185833)
- **Nodemailer**: [Nodemailer Documentation](https://nodemailer.com/)
- **This Integration**: Check application logs or contact your development team

## Resources

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Google App Passwords](https://support.google.com/accounts/answer/185833)
- [Nodemailer Documentation](https://nodemailer.com/about/)
- [Email HTML Best Practices](https://www.campaignmonitor.com/dev-resources/guides/coding/)
