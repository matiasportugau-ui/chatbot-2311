# Testing OpenAI API Best Practices Implementation

This guide explains how to test the OpenAI API best practices implementation.

## Prerequisites

1. **Environment Setup**
   ```bash
   # Set your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"
   
   # Optional: Set organization and project IDs
   export OPENAI_ORGANIZATION_ID="org-xxxxx"
   export OPENAI_PROJECT_ID="proj-xxxxx"
   
   # Optional: Configure logging
   export LOG_LEVEL="INFO"
   export ENABLE_REQUEST_TRACKING="true"
   ```

2. **Install Dependencies**
   ```bash
   pip install openai requests
   ```

## Test Scripts

### 1. Comprehensive Test Suite

Run all tests at once:

```bash
python test_openai_best_practices.py
```

This tests:
- ✅ Request tracking functionality
- ✅ Structured logging
- ✅ Rate limit monitoring
- ✅ Model integrator integration
- ✅ Debugging utilities
- ✅ API endpoints (if server is running)

### 2. Rate Limit Header Extraction Test

Test specifically for rate limit header parsing:

```bash
python test_rate_limit_extraction.py
```

This verifies:
- ✅ Rate limit header parsing
- ✅ Utilization calculations
- ✅ Warning generation
- ✅ Real API call header extraction

### 3. Structured Logging Test

Test correlation IDs and log formatting:

```bash
python test_structured_logs.py
```

This verifies:
- ✅ Correlation IDs in logs
- ✅ Log format consistency
- ✅ End-to-end logging flow

### 4. API Endpoints Test

Test the API server endpoints (requires running server):

```bash
# Start the API server first
python api_server.py

# In another terminal, run the test
./test_api_endpoints.sh

# Or manually test:
curl http://localhost:8000/api/health
curl http://localhost:8000/api/monitoring/rate-limits
curl http://localhost:8000/api/debug/request/{request_id}
```

## Manual Testing

### Test 1: Request ID Tracking

1. **Make an API call with client request ID:**
   ```python
   from model_integrator import get_model_integrator
   
   integrator = get_model_integrator()
   response = integrator.generate(
       prompt="Hello, world!",
       client_request_id="my-custom-id-123"
   )
   
   print(f"Request ID: {response.get('request_id')}")
   print(f"Client Request ID: {response.get('client_request_id')}")
   print(f"OpenAI Request ID: {response.get('openai_request_id')}")
   ```

2. **Verify in logs:**
   - Check that logs include `request_id` and `client_request_id`
   - Verify JSON format is valid

### Test 2: Rate Limit Monitoring

1. **Make multiple API calls:**
   ```python
   for i in range(5):
       response = integrator.generate(
           prompt=f"Test message {i}",
           max_tokens=10
       )
       rate_info = response.get('rate_limit_info', {})
       print(f"Call {i+1}: {rate_info.get('requests_remaining')} requests remaining")
   ```

2. **Check rate limit status:**
   ```python
   from utils.rate_limit_monitor import get_rate_limit_monitor
   
   monitor = get_rate_limit_monitor()
   limits = monitor.get_rate_limits("openai")
   
   if limits:
       print(f"Requests: {limits.requests.remaining}/{limits.requests.limit}")
       print(f"Tokens: {limits.tokens.remaining}/{limits.tokens.limit}")
   ```

### Test 3: Structured Logs

1. **Check log output:**
   - Logs should be in JSON format
   - Each log entry should include:
     - `timestamp`
     - `level`
     - `message`
     - `request_id` (when available)
     - `client_request_id` (when available)

2. **Verify correlation:**
   - All logs for the same request should have the same `request_id`
   - Request and response logs should be traceable

### Test 4: API Endpoints

1. **Health Endpoint:**
   ```bash
   curl http://localhost:8000/api/health | jq
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-...",
     "service": "bmc-chat-api",
     "rate_limits": {
       "openai:default": {
         "requests": {...},
         "tokens": {...}
       }
     }
   }
   ```

2. **Rate Limits Endpoint:**
   ```bash
   curl http://localhost:8000/api/monitoring/rate-limits | jq
   ```
   
   Expected response:
   ```json
   {
     "rate_limits": {
       "openai:default": {
         "provider": "openai",
         "requests": {
           "limit": 100,
           "remaining": 75,
           ...
         },
         "tokens": {...}
       }
     },
     "warnings": {},
     "timestamp": "..."
   }
   ```

3. **Debug Endpoint:**
   ```bash
   # First, make a request and note the request ID
   curl -X POST http://localhost:8000/chat/process \
     -H "Content-Type: application/json" \
     -H "X-Client-Request-Id: debug-test-123" \
     -d '{"mensaje": "test", "telefono": "+59812345678"}'
   
   # Then query the debug endpoint
   curl http://localhost:8000/api/debug/request/debug-test-123 | jq
   ```

## Expected Results

### ✅ Success Indicators

1. **Request Tracking:**
   - Request IDs are generated for all API calls
   - Client request IDs are validated and stored
   - Request metadata is retrievable

2. **Rate Limit Monitoring:**
   - Rate limit headers are extracted from responses
   - Utilization percentages are calculated correctly
   - Warnings are generated when approaching limits

3. **Structured Logging:**
   - All logs are in valid JSON format
   - Correlation IDs appear in all relevant logs
   - OpenAI-specific metadata is logged

4. **API Endpoints:**
   - Health endpoint returns rate limit status
   - Debug endpoint retrieves request details
   - Rate limits endpoint shows current status

### ⚠️ Common Issues

1. **Headers Not Captured:**
   - OpenAI Python SDK may not expose response headers directly
   - This is a known limitation - headers are captured when available
   - The `x-request-id` may not always be available

2. **Rate Limits Not Showing:**
   - Rate limit headers are only available after making API calls
   - Make at least one API call before checking rate limits
   - Some providers may not return all rate limit headers

3. **Request IDs Not in Logs:**
   - Ensure `ENABLE_REQUEST_TRACKING=true` is set
   - Check that request context is set before logging
   - Verify structured logger is being used

## Troubleshooting

### Issue: Tests fail with import errors

**Solution:**
```bash
# Ensure you're in the project root directory
cd /path/to/chatbot-2311

# Check that utils directory exists
ls -la utils/

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Issue: API server endpoints return 503

**Solution:**
- Ensure the API server is running
- Check that `UTILS_AVAILABLE` is True in the server
- Verify all utility modules are importable

### Issue: Rate limits always show None

**Solution:**
- Make at least one API call first
- Check that response headers are being captured
- Verify the rate limit monitor is being updated

## Next Steps

After running all tests successfully:

1. **Monitor Production Logs:**
   - Check that structured logs are being generated
   - Verify correlation IDs are working
   - Monitor rate limit warnings

2. **Set Up Alerts:**
   - Configure alerts for rate limit warnings
   - Set up monitoring for request failures
   - Track API costs and usage

3. **Optimize Configuration:**
   - Adjust rate limit warning thresholds
   - Configure request tracking retention
   - Set up log rotation and archiving

## Additional Resources

- [OpenAI API Reference](../.cursor/plans/OPENAI_API_REFERENCE.md)
- [Implementation Plan](../.cursor/plans/openai-api-best-practices-implementation.plan.md)
- Model Integrator Documentation: `model_integrator.py`
- API Server Documentation: `api_server.py`

