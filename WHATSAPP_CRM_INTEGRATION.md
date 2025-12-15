# WhatsApp Quote Engine + CRM Integration

## What Was Integrated

Your WhatsApp conversational quote engine is now **automatically integrated with the CRM system**. Every quote generated through WhatsApp is now tracked in the CRM with full customer history.

---

## How It Works

### Before Integration
1. Customer sends WhatsApp message requesting quote
2. Quote engine generates quote
3. Response sent to customer
4. ❌ No customer record created
5. ❌ No interaction history
6. ❌ No follow-up tracking

### After Integration
1. Customer sends WhatsApp message requesting quote
2. Quote engine generates quote
3. ✅ **Customer automatically created in CRM** (or retrieved if exists)
4. ✅ **Quote saved with all items and pricing**
5. ✅ **Interaction logged** (quote request + quote sent)
6. ✅ **Customer statistics updated**
7. Response sent to customer

---

## What Gets Tracked Automatically

### Customer Information
- **Phone number** (primary identifier)
- **Name** (from WhatsApp)
- **Email**: Auto-generated placeholder (`+59899123456@whatsapp.bmc.local`)
- **Source**: `whatsapp`
- **Status**: `lead` (first quote) → can be promoted to `prospect` → `customer`
- **Tags**: `whatsapp`, `auto-generated`

### Quote Details
- **Quote number**: `WA-{timestamp}` (e.g., `WA-1703001234567`)
- **Items**: All products and services with quantities and prices
- **Totals**: Subtotal, IVA, Total
- **Original consultation**: Saved in notes (first 200 characters)

### Interactions
Every quote generates 2 interactions:
1. **Quote request** (inbound) - Customer's original query
2. **Quote sent** (outbound) - Quote confirmation with details

---

## Implementation Details

### Modified File
- `src/lib/integrated-quote-engine.ts`

### Changes Made

#### 1. Import CRM Integration
```typescript
import { processQuoteWithCRM } from './crm/integrations'
```

#### 2. Auto-Integration in `procesarConsulta()`
```typescript
// After quote is generated
if (respuesta.tipo === 'cotizacion' && respuesta.cotizacion) {
  try {
    await this.integrarConCRM(respuesta.cotizacion, userPhone, userName || 'Cliente', consulta)
  } catch (crmError) {
    console.error('Error integrando con CRM (no crítico):', crmError)
    // Quote continues even if CRM fails
  }
}
```

#### 3. New Method: `integrarConCRM()`
Handles the complete CRM integration:
- Converts phone to email placeholder
- Generates unique quote number
- Extracts all quote items (products + services)
- Calls `processQuoteWithCRM()` with complete data

#### 4. New Method: `phoneToEmail()`
Converts phone numbers to CRM-compatible email format:
```typescript
+598 99 123 456 → +59899123456@whatsapp.bmc.local
```

---

## Example Flow

### Customer WhatsApp Message
```
"Hola, necesito cotizar 10 paneles Isodec de 100mm para Montevideo con flete"
```

### What Happens Automatically

1. **Quote Engine Processes**
   - Parses: 10 panels, Isodec 100mm, Montevideo zone, with shipping
   - Calculates: Product price + IVA + shipping
   - Generates AI response

2. **CRM Integration Executes**
   ```typescript
   processQuoteWithCRM({
     customerEmail: "+59899123456@whatsapp.bmc.local",
     customerName: "Juan Pérez",
     customerPhone: "+598 99 123 456",
     quoteNumber: "WA-1703001234567",
     items: [
       {
         name: "Isodec 100mm",
         quantity: 10,
         unitPrice: 150.00,
         total: 1500.00
       },
       {
         name: "Flete - Montevideo",
         quantity: 1,
         unitPrice: 200.00,
         total: 200.00
       }
     ],
     subtotal: 1500.00,
     iva: 330.00,
     total: 2030.00,
     tags: ['whatsapp', 'auto-generated'],
     notes: "Consulta original: Hola, necesito cotizar 10 paneles Isodec de 100mm para Montevideo con flete",
     source: 'whatsapp'
   })
   ```

3. **CRM Actions**
   - Creates customer record (or finds existing by phone)
   - Saves quote with all details
   - Logs "Quote Request" interaction
   - Sends quote email (if configured)
   - Logs "Quote Sent" interaction
   - Updates customer stats

4. **Response Sent to Customer**
   - Quote sent via WhatsApp
   - Everything tracked in CRM

---

## CRM Benefits

### 1. Customer History
View complete customer timeline:
```bash
GET /api/crm/customers/{id}?includeRelations=true
```

Returns:
- All quotes sent
- All interactions (WhatsApp conversations)
- Customer lifetime value
- Last contact date
- Total quotes requested

### 2. Follow-Up Tracking
Identify customers needing follow-up:
```bash
GET /api/crm/customers?status=lead&sortBy=stats.lastContactDate&sortOrder=asc
```

### 3. Conversion Analysis
- Track which quotes convert to sales
- See quote acceptance rate
- Identify high-value customers

### 4. Multi-Channel View
Customer record now includes:
- WhatsApp quotes (automatic)
- Mercado Libre orders (automatic, if ML integration active)
- Email communications (if configured)
- Manual interactions (calls, meetings)

---

## Phone-Based Email Handling

### Why Email Placeholders?
The CRM system uses email as the primary unique identifier, but WhatsApp quotes only have phone numbers. The integration creates a placeholder email to maintain CRM compatibility while using phone as the real identifier.

### Email Format
```
{clean_phone_number}@whatsapp.bmc.local
```

Examples:
- `+598 99 123 456` → `+59899123456@whatsapp.bmc.local`
- `099 123 456` → `099123456@whatsapp.bmc.local`

### Updating Later
If you collect the customer's real email later, you can update it:
```typescript
import { updateCustomer } from '@/lib/crm';

await updateCustomer(customerId, {
  email: 'real-customer@gmail.com'
});
```

The phone number remains in `customerPhone` field and continues to work as identifier.

---

## Error Handling

### Non-Blocking Integration
The CRM integration is **non-blocking** - if it fails, the quote still gets generated and sent to the customer.

```typescript
try {
  await this.integrarConCRM(...)
} catch (crmError) {
  console.error('Error integrando con CRM (no crítico):', crmError)
  // Quote continues normally
}
```

This ensures:
- Customer never sees CRM errors
- Quote delivery is never delayed
- System remains reliable even if CRM has issues

### Logging
All CRM integration events are logged:
- ✅ Success: `✅ CRM: Cliente {id} creado/actualizado con cotización {number}`
- ❌ Error: `Error integrando con CRM (no crítico): {error}`

---

## Testing the Integration

### 1. Send Test Quote via WhatsApp
Send a quote request through your WhatsApp integration

### 2. Check CRM for Customer
```bash
# Search by phone number
curl "http://localhost:3000/api/crm/customers?phone=59899123456"
```

Should return:
```json
{
  "customers": [{
    "_id": "...",
    "email": "+59899123456@whatsapp.bmc.local",
    "name": "Customer Name",
    "phone": "+598 99 123 456",
    "source": "whatsapp",
    "status": "lead",
    "tags": ["whatsapp", "auto-generated"],
    "stats": {
      "totalQuotes": 1,
      "totalRevenue": 0
    }
  }],
  "total": 1
}
```

### 3. Check Quote Record
```bash
# Get customer with relations
curl "http://localhost:3000/api/crm/customers/{id}?includeRelations=true"
```

Should include:
- Quote with all items
- Quote request interaction
- Quote sent interaction

### 4. Check Interactions
```bash
curl "http://localhost:3000/api/crm/interactions?customerId={id}"
```

Should show 2 interactions per quote:
1. Quote request (inbound)
2. Quote sent (outbound)

---

## Next Steps

### 1. Quote Acceptance Tracking
When customer accepts a quote, log it:
```typescript
import { logQuoteAcceptance } from '@/lib/crm/integrations';

await logQuoteAcceptance(
  customerId,
  quoteId,
  quoteNumber,
  totalAmount
);
// → Customer status changes to "customer"
// → Quote marked as "accepted"
// → Revenue updated
```

### 2. Follow-Up Logging
Log follow-up communications:
```typescript
import { logQuoteFollowUp } from '@/lib/crm/integrations';

await logQuoteFollowUp(
  customerId,
  quoteNumber,
  'whatsapp',
  'Customer interested, will decide by Friday'
);
```

### 3. Build CRM Dashboard
Create UI to view:
- Recent quotes
- Customers needing follow-up
- Conversion rates
- Revenue by source (WhatsApp vs Mercado Libre)

### 4. Email Collection
Update your WhatsApp flow to ask for email:
```
"Para enviarte la cotización por email, ¿cuál es tu correo?"
```

Then update CRM:
```typescript
await updateCustomer(customerId, {
  email: collectedEmail
});
```

---

## Integration Summary

✅ **Automatic**: No manual action needed, works on every quote
✅ **Non-blocking**: Won't break quotes if CRM fails
✅ **Complete**: Tracks customers, quotes, items, interactions
✅ **Phone-based**: Works with WhatsApp (no email required)
✅ **Extensible**: Ready for follow-ups, conversions, analytics

Your WhatsApp quote engine is now a complete CRM-tracked sales system!

---

## Files Modified

1. **src/lib/integrated-quote-engine.ts**
   - Added CRM integration import
   - Added auto-integration in `procesarConsulta()`
   - Added `integrarConCRM()` method
   - Added `phoneToEmail()` helper

---

## Related Documentation

- [CRM_SETUP.md](CRM_SETUP.md) - CRM system overview and API reference
- [CRM_INTEGRATION_GUIDE.md](CRM_INTEGRATION_GUIDE.md) - Complete integration guide
- [src/lib/crm/integrations/quote-integration.ts](src/lib/crm/integrations/quote-integration.ts) - Integration utilities

---

**Ready to use!** Every quote from WhatsApp is now tracked in your CRM.
