# CRM Integration Guide

Complete guide for integrating the CRM system with your quote and order workflows.

## 🎯 Quick Start - Automatic Quote Integration

The simplest way to integrate CRM with quotes:

```typescript
import { processQuoteWithCRM } from '@/lib/crm/integrations';

// When customer requests a quote
const result = await processQuoteWithCRM({
  // Customer info
  customerEmail: 'juan.perez@example.com',
  customerName: 'Juan Pérez',
  customerPhone: '+598 99 123 456',
  customerCompany: 'Constructora ABC',

  // Quote details
  quoteNumber: 'Q-2024-001',
  items: [
    {
      name: 'Panel Isodec 100mm',
      quantity: 10,
      unitPrice: 150.00
    }
  ],
  subtotal: 1500.00,
  iva: 330.00,
  total: 1830.00,
  validUntil: '2024-12-31',

  // Optional
  tags: ['construction', 'urgent'],
  notes: 'Customer prefers Monday delivery',
  source: 'email'
});

console.log(`Customer created: ${result.customerId}`);
console.log(`Email sent: ${result.emailSent}`);
```

**What this does automatically:**
1. ✅ Creates customer in CRM (or gets existing)
2. ✅ Creates quote record
3. ✅ Logs quote request interaction
4. ✅ Sends quote email
5. ✅ Logs email sent interaction
6. ✅ Updates customer statistics

---

## 📧 Integration Example 1: Quote API Endpoint

Add CRM to your quote creation API:

```typescript
// src/app/api/quotes/create/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { processQuoteWithCRM } from '@/lib/crm/integrations';

export async function POST(request: NextRequest) {
  const body = await request.json();

  try {
    // Process quote with CRM integration
    const result = await processQuoteWithCRM({
      customerEmail: body.email,
      customerName: body.name,
      customerPhone: body.phone,
      customerCompany: body.company,
      quoteNumber: body.quoteNumber || `Q-${Date.now()}`,
      items: body.items,
      subtotal: body.subtotal,
      iva: body.iva,
      total: body.total,
      validUntil: body.validUntil,
      tags: body.tags,
      notes: body.notes,
      source: 'web'
    });

    return NextResponse.json({
      success: true,
      quoteNumber: body.quoteNumber,
      customerId: result.customerId,
      emailSent: result.emailSent
    });
  } catch (error) {
    console.error('Quote creation failed:', error);
    return NextResponse.json(
      { error: 'Failed to create quote' },
      { status: 500 }
    );
  }
}
```

---

## ✅ Integration Example 2: Quote Acceptance

When customer accepts a quote:

```typescript
import { logQuoteAcceptance } from '@/lib/crm/integrations';

// After customer confirms order
await logQuoteAcceptance(
  customerId,      // from processQuoteWithCRM
  quoteId,         // from processQuoteWithCRM
  'Q-2024-001',   // quote number
  1830.00          // order amount
);
```

**What this does:**
1. ✅ Changes customer status from "lead" to "customer"
2. ✅ Updates quote status to "accepted"
3. ✅ Logs acceptance interaction
4. ✅ Updates customer revenue statistics

---

## ❌ Integration Example 3: Quote Rejection

When customer rejects a quote:

```typescript
import { logQuoteRejection } from '@/lib/crm/integrations';

await logQuoteRejection(
  customerId,
  quoteId,
  'Q-2024-001',
  'Price too high'  // optional reason
);
```

---

## 📞 Integration Example 4: Follow-ups

Log follow-up communications:

```typescript
import { logQuoteFollowUp } from '@/lib/crm/integrations';

// After calling customer
await logQuoteFollowUp(
  customerId,
  'Q-2024-001',
  'call',
  'Customer still interested, will decide by end of week'
);

// After sending email
await logQuoteFollowUp(
  customerId,
  'Q-2024-001',
  'email',
  'Sent revised quote with 10% discount'
);

// After WhatsApp message
await logQuoteFollowUp(
  customerId,
  'Q-2024-001',
  'whatsapp',
  'Confirmed delivery date for next Monday'
);
```

---

## 🛒 Integration Example 5: Mercado Libre Orders

Integrate with Mercado Libre webhook:

```typescript
// src/app/api/mercado-libre/webhook/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { processMercadoLibreOrder } from '@/lib/crm/integrations';

export async function POST(request: NextRequest) {
  const notification = await request.json();

  if (notification.topic === 'orders_v2') {
    // Fetch order from Mercado Libre
    const order = await fetchOrderFromMercadoLibre(notification.resource);

    // Integrate with CRM
    await processMercadoLibreOrder(order);
  }

  return new Response('OK', { status: 200 });
}
```

**What `processMercadoLibreOrder` does:**
1. ✅ Creates customer from Mercado Libre buyer
2. ✅ Links Mercado Libre user ID to customer
3. ✅ Sets customer status to "customer"
4. ✅ Logs order interaction
5. ✅ Updates customer revenue statistics

---

## 📦 Integration Example 6: Order Status Updates

Log shipping and delivery:

```typescript
import {
  logOrderStatusChange,
  logShippingNotification
} from '@/lib/crm/integrations';

// When order ships
await logShippingNotification(
  customerId,
  orderId,
  'TRACK-123456'
);

// When status changes
await logOrderStatusChange(
  customerId,
  orderId,
  'paid',      // old status
  'shipped'    // new status
);
```

---

## 📊 Integration Example 7: Import Existing Data

Import historical quotes:

```typescript
import { batchProcessQuotes } from '@/lib/crm/integrations';

const historicalQuotes = [
  {
    customerEmail: 'customer1@example.com',
    customerName: 'Customer 1',
    quoteNumber: 'Q-2024-001',
    items: [{ name: 'Product A', quantity: 5, unitPrice: 100 }],
    subtotal: 500,
    iva: 110,
    total: 610
  },
  // ... more quotes
];

const result = await batchProcessQuotes(historicalQuotes, {
  sendEmails: false,  // Don't send emails for historical data
  delayMs: 500,       // 500ms delay between imports
  onProgress: (processed, total) => {
    console.log(`Imported ${processed}/${total} quotes`);
  }
});

console.log(`Success: ${result.processed}, Failed: ${result.failed}`);
```

---

## 🔄 Complete Workflow Example

Full quote-to-order workflow:

```typescript
import {
  processQuoteWithCRM,
  logQuoteFollowUp,
  logQuoteAcceptance,
  promoteToProspect
} from '@/lib/crm/integrations';

// 1. Customer requests quote
const { customerId, quoteId, emailSent } = await processQuoteWithCRM({
  customerEmail: 'customer@example.com',
  customerName: 'Customer Name',
  quoteNumber: 'Q-2024-001',
  items: [...],
  subtotal: 1000,
  iva: 220,
  total: 1220,
  source: 'web'
});
// → Customer created as "lead", quote email sent

// 2. Customer asks questions (after 2 days)
await logQuoteFollowUp(
  customerId,
  'Q-2024-001',
  'email',
  'Customer asking about delivery times'
);

// 3. Customer shows strong interest
await promoteToProspect(
  customerId,
  'Multiple follow-ups, ready to purchase'
);
// → Customer status changed to "prospect"

// 4. Customer places order
await logQuoteAcceptance(
  customerId,
  quoteId,
  'Q-2024-001',
  1220.00
);
// → Customer status changed to "customer"
// → Quote marked as accepted
// → Revenue updated
```

---

## 🎨 Custom Integration Patterns

### Pattern 1: Add Custom Fields

```typescript
import { updateCustomer } from '@/lib/crm';

await updateCustomer(customerId, {
  customFields: {
    preferredDeliveryDay: 'Monday',
    paymentTerms: '30 days net',
    accountManager: 'John Doe',
    industry: 'Construction'
  }
});
```

### Pattern 2: Add Tags Dynamically

```typescript
import { getCustomerById, updateCustomer } from '@/lib/crm';

const customer = await getCustomerById(customerId);
const currentTags = customer?.tags || [];

await updateCustomer(customerId, {
  tags: [...currentTags, 'high-value', 'vip']
});
```

### Pattern 3: Manual Interactions

```typescript
import { createInteraction } from '@/lib/crm';

// Log phone call
await createInteraction({
  customerId,
  type: 'call',
  direction: 'outbound',
  subject: 'Weekly check-in',
  content: 'Discussed upcoming projects and pricing',
  tags: ['check-in', 'relationship'],
  occurredAt: new Date()
});

// Log meeting
await createInteraction({
  customerId,
  type: 'meeting',
  subject: 'Project planning meeting',
  content: 'Reviewed requirements for new warehouse',
  tags: ['meeting', 'planning']
});
```

---

## 🚀 Testing the Integration

### Test 1: Create Test Customer

```bash
curl -X POST http://localhost:3000/api/crm/customers \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test Customer",
    "getOrCreate": true
  }'
```

### Test 2: Create Quote with CRM

Create this test file: `test-quote-crm.ts`

```typescript
import { processQuoteWithCRM } from '@/lib/crm/integrations';

async function testQuoteIntegration() {
  const result = await processQuoteWithCRM({
    customerEmail: 'test@example.com',
    customerName: 'Test Customer',
    quoteNumber: 'Q-TEST-001',
    items: [
      { name: 'Test Product', quantity: 1, unitPrice: 100 }
    ],
    subtotal: 100,
    iva: 22,
    total: 122,
    tags: ['test'],
    source: 'web'
  });

  console.log('Quote processed:', result);
}

testQuoteIntegration();
```

Run: `npx ts-node test-quote-crm.ts`

### Test 3: Verify in Database

```bash
# Get customer with all data
curl "http://localhost:3000/api/crm/customers/[id]?includeRelations=true"

# Should show:
# - Customer record
# - Quote
# - Interactions (quote request, email sent)
# - Notes (if any)
# - Activity timeline
```

---

## 📋 Integration Checklist

- [ ] Install CRM dependencies (already done)
- [ ] Import `processQuoteWithCRM` in quote creation logic
- [ ] Test with sample quote
- [ ] Verify customer created in CRM
- [ ] Verify interactions logged
- [ ] Verify quote email sent
- [ ] Add quote acceptance logging
- [ ] Add follow-up logging
- [ ] Test Mercado Libre integration
- [ ] Import historical data (optional)

---

## 🎯 Best Practices

### 1. Always Use getOrCreateCustomer

Prevents duplicate customers:

```typescript
const customer = await getOrCreateCustomer({
  email: customerEmail,
  name: customerName,
  source: 'quote',
  status: 'lead'
});
```

### 2. Log All Customer Touchpoints

Every interaction matters:
- Quote sent → Log it
- Customer calls → Log it
- Email received → Log it
- Order placed → Log it

### 3. Use Meaningful Tags

Organize with tags:
```typescript
tags: ['urgent', 'wholesale', 'construction', 'vip']
```

### 4. Track Customer Journey

Update status as customer progresses:
- First contact → "lead"
- Multiple interactions → "prospect"
- First purchase → "customer"
- No activity 6 months → "inactive"

### 5. Don't Block on CRM Operations

Use try-catch to prevent CRM failures from breaking main flow:

```typescript
try {
  await processQuoteWithCRM(quoteData);
} catch (error) {
  console.error('CRM integration failed:', error);
  // Continue with quote creation anyway
}
```

---

## 🔧 Troubleshooting

### Issue: Duplicate Customers

**Solution**: Always use `getOrCreateCustomer` instead of `createCustomer`

### Issue: Missing Interactions

**Solution**: Check if `customerId` is correct and customer exists

### Issue: Email Not Sent

**Solution**: Verify SMTP credentials are configured in `.env`

### Issue: Stats Not Updating

**Solution**: Call `updateCustomerStats(customerId)` manually

---

## 📊 Next Steps

1. **Integrate with your quote form**
2. **Test with real customer data**
3. **Set up automated follow-ups**
4. **Build CRM dashboard UI**
5. **Train team on CRM usage**

The CRM is now fully integrated and ready to track all customer interactions!
