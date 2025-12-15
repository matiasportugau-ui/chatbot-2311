# Mercado Libre Integration Setup Guide

This guide will help you set up the Mercado Libre integration for your BMC chatbot platform.

## Prerequisites

- A Mercado Libre seller account
- MongoDB database configured
- Your application deployed and accessible via HTTPS (required for OAuth callback)

## Step 1: Create a Mercado Libre Application

1. Go to [Mercado Libre Developers](https://developers.mercadolibre.com.uy)
2. Log in with your Mercado Libre seller account
3. Navigate to "My Applications" or "Mis Aplicaciones"
4. Click "Create New Application" or "Crear Nueva Aplicación"
5. Fill in the application details:
   - **Name**: BMC Chatbot
   - **Short Name**: bmc-chatbot
   - **Description**: Automated quotation and sales management system
   - **Redirect URI**: `https://yourdomain.com/api/mercado-libre/auth/callback`
     - Replace `yourdomain.com` with your actual domain
     - For local development: `http://localhost:3000/api/mercado-libre/auth/callback`
   - **Scopes**: Select the following permissions:
     - `read` - Read your public data
     - `write` - Modify your data
     - `offline_access` - Access your data when you're not using the app

6. Save the application
7. Copy your credentials:
   - **App ID** (Client ID)
   - **Secret Key** (Client Secret)

## Step 2: Configure Environment Variables

Add the following variables to your `.env` file:

```bash
# Mercado Libre Configuration
MERCADO_LIBRE_APP_ID=your_app_id_here
MERCADO_LIBRE_CLIENT_SECRET=your_secret_key_here
MERCADO_LIBRE_REDIRECT_URI=https://yourdomain.com/api/mercado-libre/auth/callback
MERCADO_LIBRE_SELLER_ID=your_seller_id_here

# Optional: Webhook Secret (for receiving notifications)
MERCADO_LIBRE_WEBHOOK_SECRET=your_webhook_secret_here

# Optional: Custom API URLs (only change if using different country)
# MERCADO_LIBRE_AUTH_URL=https://auth.mercadolibre.com.uy
# MERCADO_LIBRE_API_URL=https://api.mercadolibre.com
```

### How to find your Seller ID:

1. Go to [Mercado Libre](https://mercadolibre.com.uy)
2. Log in to your account
3. Go to your profile/settings
4. Your seller ID is typically shown in your account information
5. Or use the API: `https://api.mercadolibre.com/users/me` (requires authentication)

## Step 3: Test the Configuration

### Validate Configuration

Check if your configuration is valid:

```bash
# From your project directory
curl http://localhost:3000/api/mercado-libre/config/status
```

Expected response:
```json
{
  "configured": true,
  "errors": [],
  "warnings": [],
  "status": "not_granted"
}
```

### Start OAuth Authorization

1. Start your application:
   ```bash
   npm run dev
   ```

2. Initiate the OAuth flow:
   ```bash
   curl -X POST http://localhost:3000/api/mercado-libre/auth/start \
     -H "Content-Type: application/json" \
     -d '{"returnTo": "/dashboard"}'
   ```

3. Copy the `url` from the response and open it in your browser

4. Authorize the application:
   - You'll be redirected to Mercado Libre's authorization page
   - Review the permissions requested
   - Click "Authorize" or "Autorizar"

5. You'll be redirected back to your application at the callback URL

6. Verify the grant status:
   ```bash
   curl http://localhost:3000/api/mercado-libre/config/status
   ```

   Expected response:
   ```json
   {
     "configured": true,
     "grantStatus": {
       "status": "active",
       "userId": 123456789,
       "sellerId": "YOUR_SELLER_ID",
       "expiresAt": "2025-12-15T00:00:00.000Z",
       "scope": ["read", "write", "offline_access"]
     }
   }
   ```

## Step 4: Test API Endpoints

### Fetch Your Listings

```bash
curl http://localhost:3000/api/mercado-libre/listings/fetch
```

Expected response:
```json
{
  "paging": {
    "total": 10,
    "limit": 50,
    "offset": 0
  },
  "results": [
    {
      "id": "MLU123456789",
      "title": "Panel Isodec 100mm",
      "price": 1500,
      "currency_id": "UYU",
      "status": "active",
      ...
    }
  ]
}
```

### Sync Orders

```bash
curl -X POST http://localhost:3000/api/mercado-libre/orders/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'
```

Expected response:
```json
{
  "synced": 5,
  "updated": 2,
  "new": 3,
  "total": 5
}
```

### Get Orders Summary

```bash
curl http://localhost:3000/api/mercado-libre/orders/summary
```

Expected response:
```json
{
  "total": 15,
  "pending": 2,
  "paid": 8,
  "shipped": 3,
  "delivered": 2,
  "cancelled": 0
}
```

## Step 5: Set Up Webhooks (Optional but Recommended)

Webhooks allow Mercado Libre to notify your application about order updates in real-time.

1. In your Mercado Libre application settings, add a webhook:
   - **URL**: `https://yourdomain.com/api/mercado-libre/webhook`
   - **Topics**: Select `orders` (and any others you need)

2. Generate a webhook secret:
   ```bash
   openssl rand -hex 32
   ```

3. Add the secret to your `.env`:
   ```bash
   MERCADO_LIBRE_WEBHOOK_SECRET=your_generated_secret_here
   ```

4. Configure the webhook in Mercado Libre with this secret

5. Test webhook reception:
   ```bash
   # Mercado Libre will send a verification request when you save the webhook
   # Check your application logs to see if it was received successfully
   ```

## Troubleshooting

### Error: "Invalid or expired state parameter"

- The OAuth state token expires after 15 minutes
- Restart the authorization flow from step 1

### Error: "Token exchange failed"

- Verify your `MERCADO_LIBRE_APP_ID` and `MERCADO_LIBRE_CLIENT_SECRET` are correct
- Ensure the redirect URI in your app matches the one in `.env`

### Error: "No active grant"

- You need to complete the OAuth authorization flow first
- Go to step 3 and authorize the application

### Token Expired

The integration automatically refreshes tokens when they're about to expire. If you encounter token errors:

1. Check the grant status:
   ```bash
   curl http://localhost:3000/api/mercado-libre/config/status
   ```

2. If status is "expired", re-authorize the application (step 3)

### MongoDB Connection Errors

- Verify your `MONGODB_URI` environment variable is set
- Ensure MongoDB is running and accessible
- Check database permissions

## API Endpoints Reference

### Authentication

- `POST /api/mercado-libre/auth/start` - Start OAuth flow
- `GET /api/mercado-libre/auth/callback` - OAuth callback (automatic)
- `POST /api/mercado-libre/auth/token` - Refresh token
- `GET /api/mercado-libre/config/status` - Check configuration and grant status

### Listings

- `GET /api/mercado-libre/listings/fetch` - Fetch all listings
- `GET /api/mercado-libre/listings/create` - Create new listing
- `POST /api/mercado-libre/listings/update` - Update listing
- `POST /api/mercado-libre/listings/pause` - Pause listing
- `POST /api/mercado-libre/listings/delete` - Delete listing

### Orders

- `POST /api/mercado-libre/orders/sync` - Sync orders from Mercado Libre
- `GET /api/mercado-libre/orders/summary` - Get orders summary
- `POST /api/mercado-libre/orders/acknowledge` - Acknowledge order
- `POST /api/mercado-libre/orders/ship` - Mark order as ready to ship

### Webhooks

- `POST /api/mercado-libre/webhook` - Receive webhook notifications (automatic)

## Integration Architecture

```
┌─────────────────┐
│ Mercado Libre   │
│ Marketplace     │
└────────┬────────┘
         │ OAuth 2.0
         │ API Calls
         │ Webhooks
         ▼
┌─────────────────┐
│ BMC Chatbot     │
│ Next.js App     │
├─────────────────┤
│ /lib/mercado-   │
│ libre/          │
│ - client.ts     │◄── OAuth & Token Management
│ - listings.ts   │◄── Product Listings
│ - orders.ts     │◄── Order Management
│ - webhook-      │◄── Event Processing
│   service.ts    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MongoDB         │
│ Collections:    │
│ - mercado_      │
│   libre_grants  │◄── Access Tokens
│ - mercado_      │
│   libre_orders  │◄── Order History
│ - mercado_      │
│   libre_        │◄── Webhook Events
│   webhook_      │
│   events        │
└─────────────────┘
```

## Security Best Practices

1. **Never commit credentials to git**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Use HTTPS in production**
   - OAuth requires HTTPS for redirect URIs
   - Mercado Libre enforces this for security

3. **Rotate secrets periodically**
   - Change your client secret every 6-12 months
   - Update webhook secrets regularly

4. **Validate webhook signatures**
   - The integration automatically validates HMAC signatures
   - Never disable this validation

5. **Monitor token expiration**
   - Tokens are automatically refreshed
   - Set up alerts for authentication failures

## Support

For issues with:
- **Mercado Libre API**: [Developer Forum](https://developers.mercadolibre.com.uy/support)
- **This Integration**: Check logs in `/var/log/` or application console
- **BMC Chatbot**: Contact your development team

## Next Steps

After setting up the integration:

1. [ ] Test creating a listing from your BMC quote system
2. [ ] Set up automatic order syncing (cron job or webhook)
3. [ ] Configure quote-to-listing mapping
4. [ ] Set up order status notifications to customers
5. [ ] Monitor integration health in dashboard

## Resources

- [Mercado Libre API Documentation](https://developers.mercadolibre.com.uy/en_us/api-docs)
- [OAuth 2.0 Guide](https://developers.mercadolibre.com.uy/en_us/authentication-and-authorization)
- [Orders API](https://developers.mercadolibre.com.uy/en_us/orders-management)
- [Listings API](https://developers.mercadolibre.com.uy/en_us/listings)
