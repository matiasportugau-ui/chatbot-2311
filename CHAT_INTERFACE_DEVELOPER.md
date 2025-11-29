# Chat Interface Developer Documentation

## Architecture Overview

The local chat interface system consists of three main components:

```
┌─────────────────┐
│  Browser        │
│  (HTML/JS)      │
└────────┬────────┘
         │ HTTP
         │ POST /chat/process
         ▼
┌─────────────────┐
│  FastAPI Server │
│  (api_server.py)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IA System      │
│  (ia_conversacional)│
└─────────────────┘
```

### Component Details

#### 1. Frontend (`chat-interface.html`)

**Technology**: Vanilla JavaScript, HTML5, CSS3

**Key Features**:
- Standalone HTML file (no build process)
- localStorage for persistence
- Fetch API for HTTP requests
- Event-driven architecture

**State Management**:
- `sessionId`: Current session identifier
- `messageHistory`: Array of last 100 messages
- `isLoading`: Boolean flag for request state
- `API_URL`: Configurable backend endpoint
- `DEFAULT_PHONE`: Default phone for testing

**Event Flow**:
1. User types message → `keypress` event
2. Debounce delay (300ms)
3. `handleSendMessage()` called
4. Display user message
5. Show loading indicator
6. POST to API
7. Display response or error
8. Save to history

#### 2. Backend (`api_server.py`)

**Technology**: FastAPI, Uvicorn, Python 3.8+

**Endpoints**:
- `GET /health`: Health check
- `POST /chat/process`: Process chat messages

**Request/Response Models**:
```python
class ChatRequest(BaseModel):
    mensaje: str
    telefono: str
    sesionId: Optional[str]

class ChatResponse(BaseModel):
    mensaje: str
    tipo: str
    acciones: list[str]
    confianza: float
    necesita_datos: list[str]
    sesion_id: str
    timestamp: str
```

#### 3. Orchestration (`start_chat_interface.sh`)

**Purpose**: Automated startup and management

**Functions**:
- Dependency checking
- Port detection
- Process management
- Log file creation
- Browser opening

## Code Structure

### HTML File Organization

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Meta tags, fonts, styles -->
</head>
<body>
  <!-- Chat UI structure -->
  <script>
    // Configuration
    // State variables
    // Initialization
    // Session management
    // Event listeners
    // Message handling
    // UI functions
    // Utility functions
  </script>
</body>
</html>
```

### Key Functions

#### Session Management

```javascript
getSessionId()          // Get or create session ID
clearSession()          // Clear current session
saveMessageHistory()    // Persist messages
loadMessageHistory()   // Restore messages
```

#### Message Handling

```javascript
handleSendMessage()     // Main send function with retry
displayMessage()        // Render message in UI
displayQuickActions()   // Show action buttons
displayError()          // Show error with retry option
```

#### Connection Management

```javascript
checkConnection()       // Test API availability
startConnectionMonitoring()  // Periodic health checks
updateConnectionStatus()     // Update UI indicator
```

#### Settings

```javascript
loadSettings()          // Load from localStorage
saveSettings()          // Save to localStorage
```

## Development Setup

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Dependencies
pip install -r requirements.txt
# Key: fastapi, uvicorn, pydantic
```

### Running in Development

```bash
# Terminal 1: API Server with auto-reload
uvicorn api_server:app --reload --port 8000

# Terminal 2: HTTP Server
python3 -m http.server 8080

# Browser: Open http://localhost:8080/chat-interface.html
```

### Debugging

#### Browser Console

```javascript
// Check session
console.log(sessionId);

// Check message history
console.log(messageHistory);

// Export conversation
exportConversation();

// Test connection
checkConnection();
```

#### API Logs

```bash
# Watch API logs
tail -f logs/api_server.log

# Check for errors
grep ERROR logs/api_server.log
```

#### Network Inspection

1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by "process"
4. Inspect request/response

## Code Comments & Documentation

### JSDoc Style Comments

The code includes JSDoc-style comments for major functions:

```javascript
/**
 * Send Message with Retry Logic
 * @param {number} retryAttempt - Current retry attempt (0-based)
 * @returns {Promise<void>}
 */
async function handleSendMessage(retryAttempt = 0) {
  // Implementation
}
```

### Function Documentation

All major functions are documented with:
- Purpose description
- Parameter types
- Return values
- Side effects

## Testing Guide

### Manual Testing

1. **Basic Flow**
   - Send message
   - Verify response
   - Check session persistence

2. **Error Handling**
   - Stop API server
   - Send message
   - Verify retry logic
   - Check error display

3. **Session Management**
   - Send messages
   - Reload page
   - Verify history restored

4. **Settings**
   - Change API URL
   - Save settings
   - Reload page
   - Verify persistence

5. **Accessibility**
   - Keyboard navigation
   - Screen reader testing
   - Focus management

### Automated Testing

Create test file `test_chat_interface.html`:

```javascript
// Example test structure
describe('Chat Interface', () => {
  test('Session ID generation', () => {
    // Test session ID format
  });
  
  test('Message persistence', () => {
    // Test localStorage save/load
  });
  
  test('Retry logic', () => {
    // Mock failed requests
  });
});
```

## Performance Considerations

### Optimizations Implemented

1. **Debouncing**: 300ms delay prevents duplicate sends
2. **Message Limit**: Only last 100 messages in memory
3. **Scroll Throttling**: Uses requestAnimationFrame
4. **Connection Monitoring**: 30s interval (not continuous)
5. **Retry Backoff**: Exponential delay between retries

### Memory Management

- Message history limited to 100 items
- Event listeners properly attached (no leaks)
- Cleanup on page unload
- localStorage cleanup on session clear

### Network Optimization

- Single request per message
- No polling (event-driven)
- Health checks only every 30s
- Retry with exponential backoff

## Security Considerations

### XSS Protection

```javascript
// User input is escaped
content.textContent = text;  // Not innerHTML
```

### Input Validation

- Message length checked before send
- API URL validated in settings
- Phone number format (basic check)

### LocalStorage Security

- No sensitive data stored
- Session IDs are random
- User can clear data anytime

## Extending the Interface

### Adding New Features

1. **New UI Element**
   ```javascript
   // Add to HTML
   <div id="newFeature">...</div>
   
   // Add to CSS
   #newFeature { ... }
   
   // Add to JavaScript
   document.getElementById('newFeature').addEventListener(...);
   ```

2. **New API Endpoint**
   ```javascript
   async function callNewEndpoint(data) {
     const response = await fetch(`${API_URL}/new-endpoint`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(data)
     });
     return response.json();
   }
   ```

3. **New Settings**
   ```javascript
   // Add to settings panel HTML
   <div class="settings-item">
     <label for="newSetting">New Setting:</label>
     <input type="text" id="newSetting">
   </div>
   
   // Add to loadSettings()
   document.getElementById('newSetting').value = 
     localStorage.getItem('bmc_new_setting') || 'default';
   
   // Add to saveSettings()
   localStorage.setItem('bmc_new_setting', 
     document.getElementById('newSetting').value);
   ```

### Customization Points

1. **Styling**: Edit CSS in `<style>` section
2. **API URL**: Change `API_URL` constant or use settings
3. **Retry Logic**: Modify `MAX_RETRIES` and `RETRY_DELAY`
4. **Message Limit**: Change `100` in `addToHistory()`
5. **Debounce Delay**: Change `DEBOUNCE_DELAY` constant

## Troubleshooting Development Issues

### Common Problems

#### Port Already in Use

```bash
# Find process
lsof -ti:8000

# Kill process
lsof -ti:8000 | xargs kill
```

#### CORS Errors

Check `api_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    # In production, specify exact origins
)
```

#### localStorage Quota Exceeded

- Reduce message history limit
- Clear old data periodically
- Use IndexedDB for large data

#### Event Listener Leaks

- Always remove listeners on cleanup
- Use named functions for easier removal
- Check with DevTools Memory profiler

## Best Practices

### Code Style

- Use `const`/`let` (not `var`)
- Use arrow functions for callbacks
- Use template literals for strings
- Use async/await (not callbacks)

### Error Handling

- Always use try/catch for async operations
- Provide user-friendly error messages
- Log errors to console for debugging
- Implement retry logic for network errors

### Accessibility

- Always include ARIA labels
- Support keyboard navigation
- Test with screen readers
- Provide focus indicators

### Performance

- Debounce user input
- Throttle scroll operations
- Limit data in memory
- Use requestAnimationFrame for animations

## Deployment Considerations

### Production Checklist

- [ ] Change CORS origins to specific domains
- [ ] Use HTTPS
- [ ] Add authentication
- [ ] Implement rate limiting
- [ ] Add error tracking (e.g., Sentry)
- [ ] Minify JavaScript/CSS
- [ ] Add CSP headers
- [ ] Test on multiple browsers
- [ ] Load test API endpoints

### Environment Variables

```bash
# Production API URL
export PY_CHAT_SERVICE_URL="https://api.example.com"

# Production port
export HTTP_PORT=443
```

## Contributing

### Code Changes

1. Test locally first
2. Check browser console for errors
3. Verify accessibility
4. Update documentation
5. Test on multiple browsers

### Documentation Updates

- Keep examples current
- Update troubleshooting section
- Add new features to guide
- Update API documentation

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MDN Web APIs](https://developer.mozilla.org/en-US/docs/Web/API)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

