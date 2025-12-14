/**
 * Email templates for various notification types
 */

export interface QuoteEmailData {
  customerName: string;
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
  validUntil?: string;
}

export interface OrderEmailData {
  customerName: string;
  orderNumber: string;
  orderDate: string;
  items: Array<{
    name: string;
    quantity: number;
    price: number;
  }>;
  total: number;
  shippingAddress?: string;
  trackingNumber?: string;
}

/**
 * Generate HTML for quote confirmation email
 */
export function generateQuoteEmail(data: QuoteEmailData): string {
  const itemsHtml = data.items
    .map(
      (item) => `
    <tr>
      <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">${item.name}</td>
      <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: center;">${item.quantity}</td>
      <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">$${item.unitPrice.toFixed(2)}</td>
      <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">$${item.total.toFixed(2)}</td>
    </tr>
  `
    )
    .join('');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quote Confirmation</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h1 style="color: #1f2937; margin: 0 0 10px 0;">Quote Confirmation</h1>
    <p style="color: #6b7280; margin: 0;">Quote #${data.quoteNumber}</p>
  </div>

  <div style="margin-bottom: 20px;">
    <p>Dear ${data.customerName},</p>
    <p>Thank you for your interest! Here is your quote:</p>
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
    <thead>
      <tr style="background-color: #f9fafb;">
        <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #e5e7eb;">Product</th>
        <th style="padding: 12px 8px; text-align: center; border-bottom: 2px solid #e5e7eb;">Qty</th>
        <th style="padding: 12px 8px; text-align: right; border-bottom: 2px solid #e5e7eb;">Unit Price</th>
        <th style="padding: 12px 8px; text-align: right; border-bottom: 2px solid #e5e7eb;">Total</th>
      </tr>
    </thead>
    <tbody>
      ${itemsHtml}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="3" style="padding: 8px; text-align: right; font-weight: bold;">Subtotal:</td>
        <td style="padding: 8px; text-align: right;">$${data.subtotal.toFixed(2)}</td>
      </tr>
      <tr>
        <td colspan="3" style="padding: 8px; text-align: right; font-weight: bold;">IVA (22%):</td>
        <td style="padding: 8px; text-align: right;">$${data.iva.toFixed(2)}</td>
      </tr>
      <tr style="background-color: #f9fafb;">
        <td colspan="3" style="padding: 12px 8px; text-align: right; font-weight: bold; font-size: 18px;">Total:</td>
        <td style="padding: 12px 8px; text-align: right; font-weight: bold; font-size: 18px; color: #059669;">$${data.total.toFixed(2)}</td>
      </tr>
    </tfoot>
  </table>

  ${
    data.validUntil
      ? `<p style="color: #6b7280; font-style: italic;">This quote is valid until ${data.validUntil}</p>`
      : ''
  }

  <div style="background-color: #eff6ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
    <p style="margin: 0; font-weight: bold;">Next Steps:</p>
    <ul style="margin: 10px 0 0 0;">
      <li>Review the quote details above</li>
      <li>Reply to this email if you have any questions</li>
      <li>Confirm your order to proceed with purchase</li>
    </ul>
  </div>

  <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
    <p>Best regards,<br>BMC Team</p>
    <p style="font-size: 12px; color: #9ca3af;">
      This is an automated email. Please do not reply directly to this message.
      If you have any questions, please contact us at your convenience.
    </p>
  </div>
</body>
</html>
  `;
}

/**
 * Generate plain text version of quote email
 */
export function generateQuoteTextEmail(data: QuoteEmailData): string {
  const itemsText = data.items
    .map(
      (item) =>
        `${item.name} - Qty: ${item.quantity} x $${item.unitPrice.toFixed(2)} = $${item.total.toFixed(2)}`
    )
    .join('\n');

  return `
Quote Confirmation
Quote #${data.quoteNumber}

Dear ${data.customerName},

Thank you for your interest! Here is your quote:

${itemsText}

Subtotal: $${data.subtotal.toFixed(2)}
IVA (22%): $${data.iva.toFixed(2)}
Total: $${data.total.toFixed(2)}

${data.validUntil ? `This quote is valid until ${data.validUntil}` : ''}

Next Steps:
- Review the quote details above
- Reply to this email if you have any questions
- Confirm your order to proceed with purchase

Best regards,
BMC Team

---
This is an automated email. Please do not reply directly to this message.
If you have any questions, please contact us at your convenience.
  `.trim();
}

/**
 * Generate HTML for order confirmation email
 */
export function generateOrderEmail(data: OrderEmailData): string {
  const itemsHtml = data.items
    .map(
      (item) => `
    <tr>
      <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">${item.name}</td>
      <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: center;">${item.quantity}</td>
      <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">$${item.price.toFixed(2)}</td>
    </tr>
  `
    )
    .join('');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Order Confirmation</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background-color: #dcfce7; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h1 style="color: #15803d; margin: 0 0 10px 0;">Order Confirmed! 🎉</h1>
    <p style="color: #16a34a; margin: 0;">Order #${data.orderNumber}</p>
  </div>

  <div style="margin-bottom: 20px;">
    <p>Dear ${data.customerName},</p>
    <p>Thank you for your order! We're processing it now and will ship it soon.</p>
  </div>

  <div style="background-color: #f9fafb; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
    <p style="margin: 0 0 5px 0;"><strong>Order Date:</strong> ${data.orderDate}</p>
    ${
      data.shippingAddress
        ? `<p style="margin: 5px 0;"><strong>Shipping Address:</strong><br>${data.shippingAddress}</p>`
        : ''
    }
    ${
      data.trackingNumber
        ? `<p style="margin: 5px 0;"><strong>Tracking Number:</strong> ${data.trackingNumber}</p>`
        : ''
    }
  </div>

  <h2 style="color: #1f2937; font-size: 18px; margin-bottom: 10px;">Order Items</h2>

  <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
    <thead>
      <tr style="background-color: #f9fafb;">
        <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #e5e7eb;">Product</th>
        <th style="padding: 12px 8px; text-align: center; border-bottom: 2px solid #e5e7eb;">Qty</th>
        <th style="padding: 12px 8px; text-align: right; border-bottom: 2px solid #e5e7eb;">Price</th>
      </tr>
    </thead>
    <tbody>
      ${itemsHtml}
    </tbody>
    <tfoot>
      <tr style="background-color: #f9fafb;">
        <td colspan="2" style="padding: 12px 8px; text-align: right; font-weight: bold; font-size: 18px;">Total:</td>
        <td style="padding: 12px 8px; text-align: right; font-weight: bold; font-size: 18px; color: #059669;">$${data.total.toFixed(2)}</td>
      </tr>
    </tfoot>
  </table>

  <div style="background-color: #eff6ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
    <p style="margin: 0; font-weight: bold;">What happens next?</p>
    <ul style="margin: 10px 0 0 0;">
      <li>We're preparing your order for shipment</li>
      <li>You'll receive a shipping confirmation with tracking details</li>
      <li>Estimated delivery: 3-5 business days</li>
    </ul>
  </div>

  <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
    <p>Thank you for your business!<br>BMC Team</p>
    <p style="font-size: 12px; color: #9ca3af;">
      Questions about your order? Reply to this email and we'll be happy to help.
    </p>
  </div>
</body>
</html>
  `;
}

/**
 * Generate plain text version of order email
 */
export function generateOrderTextEmail(data: OrderEmailData): string {
  const itemsText = data.items
    .map((item) => `${item.name} - Qty: ${item.quantity} - $${item.price.toFixed(2)}`)
    .join('\n');

  return `
Order Confirmed!
Order #${data.orderNumber}

Dear ${data.customerName},

Thank you for your order! We're processing it now and will ship it soon.

Order Date: ${data.orderDate}
${data.shippingAddress ? `Shipping Address: ${data.shippingAddress}` : ''}
${data.trackingNumber ? `Tracking Number: ${data.trackingNumber}` : ''}

Order Items:
${itemsText}

Total: $${data.total.toFixed(2)}

What happens next?
- We're preparing your order for shipment
- You'll receive a shipping confirmation with tracking details
- Estimated delivery: 3-5 business days

Thank you for your business!
BMC Team

---
Questions about your order? Reply to this email and we'll be happy to help.
  `.trim();
}
