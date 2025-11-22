# Sentry Integration Guide

This document explains how to set up and use Sentry error tracking in the ai-mem project.

## Overview

Sentry is integrated into the ai-mem application to provide:
- **Error Tracking**: Automatic capture of exceptions and errors
- **Performance Monitoring**: Track API endpoint performance
- **Logging Integration**: Capture ERROR-level logs automatically
- **Custom Context**: Add user and request context to errors

## Setup Instructions

### 1. Access Your Self-Hosted Sentry

1. Open your browser and go to: **http://localhost:9000**
2. Log in with your credentials:
   - Email: `tranvantri2000@gmail.com`
   - Password: (the one you set during installation)

### 2. Create a New Project

1. Click **"Create Project"** or go to **Settings > Projects > Create Project**
2. Select **Python** as the platform
3. Select **FastAPI** as the framework (or just Python if FastAPI isn't listed)
4. Name your project: `ai-mem` (or any name you prefer)
5. Click **"Create Project"**

### 3. Get Your DSN (Data Source Name)

After creating the project, you'll see a DSN that looks like:
```
http://PUBLIC_KEY@localhost:9000/PROJECT_ID
```

**Example:**
```
http://abc123def456@localhost:9000/2
```

Copy this DSN - you'll need it for configuration.

### 4. Configure Environment Variables

1. Copy the example environment file (if you haven't already):
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update the Sentry configuration:
   ```bash
   # Sentry Configuration
   SENTRY_DSN=http://YOUR_PUBLIC_KEY@localhost:9000/YOUR_PROJECT_ID
   SENTRY_ENVIRONMENT=development
   SENTRY_TRACES_SAMPLE_RATE=1.0
   SENTRY_PROFILES_SAMPLE_RATE=1.0
   ```

   **Configuration Options:**
   - `SENTRY_DSN`: Your Sentry DSN (required)
   - `SENTRY_ENVIRONMENT`: Environment name (development, staging, production)
   - `SENTRY_TRACES_SAMPLE_RATE`: Percentage of requests to track (0.0 to 1.0)
     - `1.0` = 100% (recommended for development)
     - `0.1` = 10% (recommended for production)
   - `SENTRY_PROFILES_SAMPLE_RATE`: Percentage of requests to profile (0.0 to 1.0)

### 5. Verify Installation

1. Start your application:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```

2. Check the logs - you should see:
   ```
   INFO - Sentry initialized successfully - Environment: development, Traces: 100.0%, Profiles: 100.0%
   ```

3. Test error tracking by triggering an error in your API

## Usage Examples

### Automatic Error Tracking

All unhandled exceptions in FastAPI endpoints are automatically captured:

```python
@router.get("/test-error")
async def test_error():
    # This error will be automatically sent to Sentry
    raise ValueError("This is a test error!")
```

### Manual Error Capture

```python
from ai_mem.server.infrastructure.sentry_config import capture_exception

try:
    # Some risky operation
    result = risky_operation()
except Exception as e:
    # Manually capture with extra context
    capture_exception(e, user_id="123", operation="risky_operation")
```

### Capture Messages

```python
from ai_mem.server.infrastructure.sentry_config import capture_message

# Log important events
capture_message(
    "User performed critical action",
    level="warning",
    user_id="123",
    action="delete_all_data"
)
```

### Set User Context

```python
from ai_mem.server.infrastructure.sentry_config import set_user_context

# Add user information to all subsequent errors
set_user_context(
    user_id="user_123",
    email="user@example.com",
    username="john_doe"
)
```

### Set Custom Context

```python
from ai_mem.server.infrastructure.sentry_config import set_context

# Add custom context to errors
set_context("database", {
    "query": "SELECT * FROM memories",
    "execution_time": 1.5,
    "rows_returned": 100
})
```

## Testing Sentry Integration

### 1. Create a Test Endpoint

Add this to your router for testing:

```python
from ai_mem.server.infrastructure.sentry_config import (
    capture_exception,
    capture_message,
    set_user_context
)

@router.get("/test-sentry")
async def test_sentry():
    """Test endpoint to verify Sentry integration"""
    
    # Test 1: Capture a message
    capture_message("Sentry test message", level="info")
    
    # Test 2: Set user context
    set_user_context(user_id="test_user", email="test@example.com")
    
    # Test 3: Trigger an error
    try:
        1 / 0
    except Exception as e:
        capture_exception(e, test_type="division_by_zero")
    
    return {"status": "Sentry test completed - check your Sentry dashboard!"}
```

### 2. Test the Endpoint

```bash
curl http://localhost:8000/api/v1/ai-mem/test-sentry
```

### 3. Check Sentry Dashboard

1. Go to http://localhost:9000
2. Navigate to **Issues** in your project
3. You should see the captured error and message

## Performance Monitoring

Sentry automatically tracks:
- **API Endpoint Performance**: Response times for all endpoints
- **Database Queries**: Execution time and query details
- **External API Calls**: HTTP request performance

View performance data in Sentry:
1. Go to **Performance** in the Sentry dashboard
2. See transaction traces and slow endpoints
3. Identify performance bottlenecks

## Best Practices

### 1. Environment-Specific Configuration

**Development:**
```bash
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0  # Track 100% of requests
```

**Production:**
```bash
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Track 10% of requests (reduce overhead)
```

### 2. Sensitive Data

The integration is configured with `send_default_pii=False` to avoid sending:
- User passwords
- API keys
- Personal information

If you need to send user data, do it explicitly using `set_user_context()`.

### 3. Error Filtering

Not all errors need to be tracked. You can filter errors in your code:

```python
try:
    result = operation()
except ValueError as e:
    # Don't send validation errors to Sentry
    logger.warning(f"Validation error: {e}")
except Exception as e:
    # Send unexpected errors to Sentry
    capture_exception(e)
```

### 4. Performance Impact

- In development: Use 100% sampling for complete visibility
- In production: Use 10-20% sampling to reduce overhead
- Sentry SDK is designed to have minimal performance impact

## Troubleshooting

### Sentry Not Initializing

**Symptom:** Log shows "Sentry DSN not configured, skipping Sentry initialization"

**Solution:**
1. Check that `.env` file exists
2. Verify `SENTRY_DSN` is set correctly
3. Ensure DSN doesn't contain placeholder text

### Errors Not Appearing in Dashboard

**Possible causes:**
1. **Wrong DSN**: Verify the DSN matches your project
2. **Network issues**: Check that localhost:9000 is accessible
3. **Sentry not running**: Ensure `docker compose up -d` is running
4. **Sampling**: If sample rate is < 1.0, not all errors are sent

**Debug:**
```python
import sentry_sdk
print(sentry_sdk.Hub.current.client)  # Should not be None
```

### Performance Data Not Showing

**Solution:**
- Ensure `SENTRY_TRACES_SAMPLE_RATE` > 0
- Wait a few minutes for data to appear
- Check the Performance tab in Sentry dashboard

## Additional Resources

- [Sentry Python SDK Documentation](https://docs.sentry.io/platforms/python/)
- [FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Self-Hosted Sentry Docs](https://develop.sentry.dev/self-hosted/)

## Support

For issues with:
- **Sentry Integration**: Check this documentation
- **Self-Hosted Sentry**: See `/self-hosted/README.md`
- **Application Errors**: Check application logs in `logs/` directory
