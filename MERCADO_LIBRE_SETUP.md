# Mercado Libre OAuth Setup Guide

## ✅ Configuration Complete

Your Mercado Libre app credentials have been configured:
- App ID: `742811153438318`
- Client Secret: `L9EGZShXy5xXLHVI9Zm8lKbgvX8bCbK5`
- Redirect URI: `https://bmc-cotizacion-inteligente.vercel.app/api/mercado-libre/auth/callback`

## 🚀 Next Steps

You have two options to complete the OAuth flow:

### Option 1: Test Locally (Recommended First)

1. **Add localhost redirect URI to your Mercado Libre app:**
   - Go to https://developers.mercadolibre.com.uy/
   - Edit your app configuration
   - Add this redirect URI: `http://localhost:3000/api/mercado-libre/auth/callback`
   - Save changes

2. **Update your .env file:**
   ```bash
   # Change this line temporarily for local testing:
   MERCADO_LIBRE_REDIRECT_URI=http://localhost:3000/api/mercado-libre/auth/callback
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Generate and visit the OAuth URL:**
   ```bash
   npm run meli-auth
   ```
   Copy the URL from the output and open it in your browser.

5. **Authorize the app:**
   - Login to Mercado Libre
   - Click "Autorizar"
   - You'll be redirected back to localhost
   - Tokens will be automatically saved to MongoDB

### Option 2: Deploy to Vercel (Production)

1. **Deploy your app to Vercel:**
   ```bash
   vercel --prod
   ```

2. **Set environment variables in Vercel:**
   - Go to your Vercel project settings
   - Add all environment variables from your .env file
   - Redeploy if necessary

3. **Generate and visit the OAuth URL:**
   ```bash
   npm run meli-auth
   ```

4. **Authorize the app:**
   - The redirect URI is already configured for Vercel
   - Click "Autorizar" when prompted
   - You'll be redirected to your Vercel app
   - Tokens will be saved to MongoDB

## 🔍 Verify OAuth Success

After completing OAuth, verify the grant was saved:

```bash
# Check MongoDB for the grant
mongosh "mongodb+srv://matiasportugau_db_user:Metallica123123@cluster0.kek5hdd.mongodb.net/bmc_quotes"

# In mongosh:
use bmc_quotes
db.mercado_libre_grants.find().pretty()
```

You should see a document with:
- `sellerId`
- `accessToken`
- `refreshToken`
- `expiresAt`

## 🤖 Test the Automation

Once OAuth is complete, test the automation:

```bash
# Run manually
npm run mercado-auto

# Or trigger the launchd service
launchctl start com.mercado.auto

# Check the logs
tail -50 ~/Library/Logs/mercado-auto.log
```

The automation will now fetch **real unanswered questions** from Mercado Libre!

## 📝 Quick Commands

- `npm run meli-auth` - Generate OAuth authorization URL
- `npm run dev` - Start development server
- `npm run mercado-auto` - Run Mercado Libre automation manually
- `launchctl start com.mercado.auto` - Trigger automation via launchd

## 🔄 Token Refresh

Tokens are automatically refreshed when they expire. The system handles this for you!

## 🆘 Troubleshooting

If you get "No active grant found":
1. Make sure you completed the OAuth flow
2. Check MongoDB for the grant document
3. Verify the grant hasn't expired

If OAuth fails:
1. Check that redirect URIs match in Mercado Libre app config
2. Verify MongoDB connection
3. Check browser console for errors
