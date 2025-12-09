# Railway Perfect Deployment Guide (Hybrid Python + Next.js)

This guide explains how to deploy the `chatbot-2311` project as two separate, optimized services on Railway.

## 1. Prerequisites
- A Railway account.
- The GitHub repository connected to Railway.

## 2. Service 1: Backend (Python)
This service runs the FastAPI backend.

1.  **Create New Service**: In your Railway project, click `New` -> `GitHub Repo` -> Select this repository.
2.  **Configuration**:
    - Railway should automatically detect `railway.json`.
    - **Verify settings**:
        - **Build Command**: `pip install -r requirements.txt && python3 -m playwright install --with-deps chromium`
        - **Start Command**: `uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port $PORT`
3.  **Variables**:
    - Add all your environment variables (from `.env`).
    - **CRITICAL**: Set `PORT` (Railway provides this, but ensure your app listens on it).

## 3. Service 2: Frontend (Next.js)
This service runs the Next.js frontend.

1.  **Create New Service**: In the SAME Railway project, click `New` -> `GitHub Repo` -> Select this repository (AGAIN).
2.  **Configuration**:
    - Go to `Settings` -> `Service` -> `Source`.
    - **Root Directory**: Leave as `/` (since `package.json` is in root).
    - **Docker Path**: `Dockerfile` (This tells Railway to use the specific Dockerfile we optimized).
3.  **Variables**: 
    - `NEXT_PUBLIC_API_URL`: Point this to the **Public Domain** of your Backend Service (e.g., `https://backend-production.up.railway.app`).

## 4. Networking
- **Backend**:
    - Go to `Settings` -> `Networking`.
    - Click `Generate Domain` (or add custom domain) to expose the API.
- **Frontend**:
    - Go to `Settings` -> `Networking`.
    - Click `Generate Domain` (or add custom domain) to expose the UI.

## 5. Verification
- **Backend**: Visit `https://<backend-url>/docs` to see Swagger UI.
- **Frontend**: Visit `https://<frontend-url>` to see the Chat Interface.

## Troubleshooting
- **Build Fails (Frontend)**: Ensure `next.config.js` has `output: 'standalone'`.
- **Connection Refused**: Check that Frontend `NEXT_PUBLIC_API_URL` uses `https` and matches the Backend URL exactly (no trailing slash usually preferred).
