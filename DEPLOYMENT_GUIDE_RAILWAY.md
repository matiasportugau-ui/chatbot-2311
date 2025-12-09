# Deployment Guide: Going Cloud-Based (Railway & Render)

You asked about keeping your bot running even when your computer is off. To do this, we need to deploy your code to a cloud provider.

I have configured your project to work seamlessly with **Railway** or **Render**. Both are excellent choices.

## Option 1: Railway (Recommended for Ease of Use)

1.  **Create an Account**: Go to [railway.app](https://railway.app/) and sign up (GitHub login recommended).
2.  **New Project**: Click "New Project" -> "Deploy from GitHub repo".
3.  **Select Repository**: Choose your `chatbot2511` repository.
4.  **Variables**: Railway usually auto-detects variables, but you should manually verify:
    *   `OPENAI_API_KEY`: Paste your key here.
    *   `MONGODB_URI`: Railway can provision a MongoDB for you. Right-click the project -> "New" -> "Database" -> "MongoDB". Then copy the connection string into your chatbot service variables.
5.  **Deploy**: Railway will automatically build and deploy using the `railway.json` file I updated.

## Option 2: Render

1.  **Create an Account**: Go to [render.com](https://render.com/).
2.  **New Web Service**: Click "New +" -> "Web Service".
3.  **Connect GitHub**: Select your repository.
4.  **Runtime**: It should detect "Python 3".
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `python unified_launcher.py --mode fullstack --production --non-interactive` (This should be auto-filled from `render.yaml`).
7.  **Environment Variables**: Add your `OPENAI_API_KEY` and `MONGODB_URI`.

## Important Note on "Persistence"

Once deployed, your bot runs on their servers.
*   **Discord/WhatsApp**: Will work 24/7.
*   **Web Interface**: You will get a NEW public URL (e.g., `https://chatbot-production.up.railway.app`). You can use this link from your phone or any computer.

## Verification
After deployment, visit the URL provided by Railway/Render. You should see the login screen or dashboard, confirming the full stack is running.
