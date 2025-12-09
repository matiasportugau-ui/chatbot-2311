
# 🚀 BMC Chatbot - Deployment Guide (Observational Mode)

This guide explains how to deploy the BMC Chatbot in **Observational Mode** (Listen Only) and how to manage the WhatsApp integration online.

## 📋 Status: v1.0 Observational
- **Branch**: `release/v1.0-observational`
- **Current Mode**: `LISTEN_ONLY_MODE=true`
- **Function**: Receives WhatsApp messages, processes them with AI/RAG, logs them to MongoDB, but **does NOT reply**.

---

## ☁️ Deployment Methods

### Option 1: Railway / Render (Recommended)

1. **Connect GitHub**:
   - Link your `release/v1.0-observational` branch to a new service on Railway or Render.

2. **Build Command**:
   - `pip install -r requirements.txt`

3. **Start Command**:
   - `python3 integracion_whatsapp.py --servidor`
   - *Note: Ensure the service listens on port `PORT` provided by the cloud environment.*

4. **Environment Variables**:
   Set the following variables in your Cloud Dashboard (do NOT check these into Git):

   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `OPENAI_API_KEY` | `sk-...` | Your OpenAI Key |
   | `WHATSAPP_ACCESS_TOKEN` | `EA...` | WhatsApp Business Token |
   | `WHATSAPP_PHONE_NUMBER_ID` | `...` | Valid Phone ID |
   | `WHATSAPP_VERIFY_TOKEN` | `...` | Your custom verify token |
   | `WHATSAPP_WEBHOOK_SECRET` | `...` | Secret for signature validation |
   | `MONGODB_URI` | `mongodb+srv://...` | Connection string |
   | `LISTEN_ONLY_MODE` | `true` | **CRITICAL**: Keeps bot silent |
   | `PORT` | `5000` | Typically auto-set by provider |

---

## 🔗 WhatsApp Webhook Configuration

Once deployed, you will get a public URL (e.g., `https://bmc-chatbot.railway.app`).

1. Go to [Meta for Developers](https://developers.facebook.com/).
2. Select your App -> WhatsApp -> Configuration.
3. Edit **Webhook**:
   - **Callback URL**: `https://<YOUR-APP-URL>/webhook`
   - **Verify Token**: Must match `WHATSAPP_VERIFY_TOKEN`.
4. **Subscribe** to `messages` field.

---

## 🛠 Operation & Monitoring

### Switching to Active Mode (Reply to Users)
When you are ready to let the bot reply:
1. Go to your Cloud Dashboard Variables.
2. Change `LISTEN_ONLY_MODE` to `false`.
3. Redeploy.

### Logs
- Check `stdout` / Application Logs for:
  - `🔇 MODO ESCUCHA`: Messages processed but not sent.
  - `✅ Interacción registrada`: Successful DB save.

---

## 📦 Files for Deployment
- `integracion_whatsapp.py`: Main entry point.
- `requirements.txt`: Python dependencies.
- `base_conocimiento_dinamica.py`: Knowledge base logic.
- `ia_conversacional_integrada.py`: AI Logic.
