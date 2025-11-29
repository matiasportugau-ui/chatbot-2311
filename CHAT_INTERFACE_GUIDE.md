# Local Chat Interface Guide

## Overview

The local HTML chat interface (`chat-interface.html`) is a standalone, production-like UI for testing and training the BMC chatbot locally. It connects to the FastAPI backend at `http://localhost:8000/chat/process` and provides a complete chat experience with session management, message persistence, and advanced features.

## Quick Start

### Prerequisites

- Python 3.8+ installed
- FastAPI dependencies installed (`pip install -r requirements.txt`)
- API server (`api_server.py`) available

### Running the System

1. **Automatic Startup (Recommended)**
   ```bash
   bash start_chat_interface.sh
   ```
   This script will:
   - Check prerequisites
   - Install dependencies if needed
   - Start the API server on port 8000
   - Start the HTTP server on an available port (default 8080)
   - Open your browser automatically

2. **Manual Startup**
   ```bash
   # Terminal 1: Start API server
   python3 api_server.py
   
   # Terminal 2: Start HTTP server
   python3 -m http.server 8080
   
   # Then open: http://localhost:8080/chat-interface.html
   ```

### Accessing the Interface

- **Default URL**: `http://localhost:8080/chat-interface.html`
- The script will display the exact URL when it starts
- If auto-open fails, manually navigate to the displayed URL

## Features

### Core Functionality

- **Real-time Chat**: Send messages and receive AI-powered responses
- **Session Management**: Persistent session IDs stored in localStorage
- **Message History**: Messages persist across page reloads (last 100 messages)
- **Quick Actions**: Clickable buttons for common responses
- **Connection Status**: Visual indicator showing API connection state
- **Retry Logic**: Automatic retry (up to 3 attempts) on failed requests
- **Error Handling**: User-friendly error messages with retry options

### Advanced Features

- **Settings Panel**: Configure API URL and default phone number
- **Export/Import**: Export conversations as JSON files
- **Browser Notifications**: Get notified when bot responds (if tab is inactive)
- **Accessibility**: Full ARIA labels, keyboard navigation, screen reader support
- **Responsive Design**: Works on desktop and mobile devices
- **Debounced Input**: Prevents duplicate message sends

## Configuration

### Settings Panel

Click the menu button (⋯) in the header to access settings:

- **API URL**: Backend endpoint (default: `http://localhost:8000/chat/process`)
- **Phone Number**: Default phone for testing (default: `+59891234567`)

Settings are saved to localStorage and persist across sessions.

### Environment Variables

The startup script supports these environment variables:

```bash
# Custom API URL
export PY_CHAT_SERVICE_URL="http://your-server:8000"
bash start_chat_interface.sh

# Custom HTTP port
export HTTP_PORT=3000
bash start_chat_interface.sh
```

## Production Rollout

Once the FastAPI backend is deployed (via `scripts/run_full_stack.sh`, Docker Compose, or systemd), you can expose the chat UI with any static server:

1. **Reuse the startup script for demos**
   ```bash
   CHAT_REFRESH_ON_START=true PY_CHAT_SERVICE_URL="https://api.example.com" bash start_chat_interface.sh
   ```
   This refreshes the knowledge base and serves `chat-interface.html` locally. Share the printed URL or tunnel it with ngrok.

2. **Serve statically with Nginx/Apache**
   - Copy `chat-interface.html` (and related assets) to your web root.
   - Ensure the in-app settings or `PY_CHAT_SERVICE_URL` point to your deployed API (`https://api.example.com/chat/process`).
   - Sample Nginx block:
     ```nginx
     server {
       listen 80;
       server_name chat.example.com;
       root /var/www/bmc-chat;
       location / {
         try_files $uri $uri/ =404;
       }
       location /chat/process {
         proxy_pass http://127.0.0.1:8000/chat/process;
         proxy_set_header Host $host;
         proxy_set_header X-Forwarded-Proto $scheme;
       }
     }
     ```

3. **Static hosting/CDN**
   - Upload the HTML to S3, Cloud Storage, Netlify, etc.
   - Configure CORS so the browser is allowed to reach the FastAPI endpoint.
   - Keep `.env` in sync on the backend to preserve MongoDB persistence and Mercado Libre ingestion.

## API Integration

### Request Format

```json
{
  "mensaje": "User message text",
  "telefono": "+59891234567",
  "sesionId": "session_1234567890_abc123"
}
```

### Response Format

```json
{
  "mensaje": "Bot response text",
  "tipo": "informativa",
  "acciones": ["Option 1", "Option 2"],
  "confianza": 0.9,
  "necesita_datos": [],
  "sesion_id": "session_1234567890_abc123",
  "timestamp": "2025-11-26T03:36:42.925794"
}
```

## Troubleshooting

### Common Issues

#### API Server Not Starting

**Problem**: Health check fails, connection status shows "Disconnected"

**Solutions**:
1. Check if port 8000 is available: `lsof -ti:8000`
2. Verify dependencies: `python3 -c "import fastapi, uvicorn"`
3. Check logs: `tail -f logs/api_server.log`
4. Start manually: `python3 api_server.py`

#### HTTP Server Port Conflict

**Problem**: Script can't find available port

**Solutions**:
1. Kill existing server: `lsof -ti:8080 | xargs kill`
2. Use custom port: `export HTTP_PORT=3000`
3. Check port range: Script tries ports 8080-8090

#### CORS Errors

**Problem**: Browser console shows CORS errors

**Solutions**:
1. Verify API server CORS config in `api_server.py`
2. Check API URL in settings matches actual server
3. Ensure API server is running before opening interface

#### Messages Not Persisting

**Problem**: Messages disappear on page reload

**Solutions**:
1. Check browser localStorage is enabled
2. Clear browser cache and try again
3. Check browser console for errors
4. Verify localStorage quota not exceeded

#### Connection Status Always Disconnected

**Problem**: Status shows disconnected even when API works

**Solutions**:
1. Check health endpoint: `curl http://localhost:8000/health`
2. Verify API URL in settings
3. Check browser console for network errors
4. Disable browser extensions that might block requests

## Training & Testing Tips

### Session Management

- Each browser session gets a unique session ID
- Session IDs persist in localStorage
- Clear session via close button (×) in header
- Session ID format: `session_<timestamp>_<random>`

### Message History

- Last 100 messages are stored in localStorage
- History persists across page reloads
- Export conversations for analysis
- Import previous conversations for testing

### Testing Workflows

1. **Quick Testing**: Use default phone number and session
2. **Multi-turn Conversations**: Keep session active, test context retention
3. **Error Scenarios**: Stop API server to test error handling
4. **Performance**: Send rapid messages to test debouncing
5. **Accessibility**: Use keyboard navigation and screen readers

### Exporting Conversations

In browser console:
```javascript
exportConversation()
```

This downloads a JSON file with:
- Session ID
- Complete message history
- Export timestamp

### Logs

Check logs for debugging:
- **API Server**: `logs/api_server.log`
- **HTTP Server**: `logs/http_server.log`

## Development

### File Structure

```
chat-interface.html          # Main HTML file (standalone)
start_chat_interface.sh      # Startup orchestration script
api_server.py                # FastAPI backend
logs/                        # Log files (created automatically)
```

### Customization

#### Changing Default Phone

Edit `chat-interface.html`:
```javascript
const DEFAULT_PHONE = '+59891234567'; // Change this
```

Or use Settings panel in UI.

#### Changing API URL

Edit `chat-interface.html`:
```javascript
const API_URL = 'http://localhost:8000/chat/process'; // Change this
```

Or use Settings panel in UI.

#### Styling

All styles are in the `<style>` section of `chat-interface.html`. Key classes:
- `.chat-container` - Main container
- `.message-wrapper` - Individual messages
- `.quick-actions` - Action buttons
- `.connection-status` - Status indicator

## API Endpoints

### Health Check
```
GET /health
```

### Process Message
```
POST /chat/process
Content-Type: application/json

{
  "mensaje": "Hello",
  "telefono": "+59891234567",
  "sesionId": "session_123"
}
```

## Browser Compatibility

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Security Notes

- **Local Only**: This interface is designed for local development/testing
- **No Authentication**: No user authentication required
- **CORS**: Configured for localhost only
- **XSS Protection**: User input is escaped before display
- **No HTTPS**: Not intended for production use

## Performance

- **Message Limit**: Last 100 messages kept in memory
- **Debouncing**: 300ms delay on message send
- **Retry Logic**: Up to 3 retries with exponential backoff
- **Connection Check**: Every 30 seconds
- **Scroll Optimization**: Uses requestAnimationFrame

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review browser console for errors
3. Verify API server is running: `curl http://localhost:8000/health`
4. Check this guide's troubleshooting section

## Next Steps

- Test various conversation flows
- Export conversations for training data
- Customize UI/UX as needed
- Integrate with production backend for testing
- Use for training and validation of AI responses

