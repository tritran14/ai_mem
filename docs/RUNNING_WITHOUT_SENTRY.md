# Running Without Sentry

The ai-mem application is designed to work seamlessly **with or without** Sentry error tracking configured.

## Default Behavior (No Sentry)

If you don't configure Sentry (no `SENTRY_DSN` in `.env`), the application will:

✅ **Run normally** - All features work as expected  
✅ **No warnings** - Silent operation without Sentry  
✅ **No errors** - All Sentry functions are safe to call  
✅ **No overhead** - Zero performance impact  

## How It Works

### 1. Silent Initialization

When Sentry is not configured:
```python
# This logs at DEBUG level (not visible in production)
logger.debug("Sentry DSN not configured, running without error tracking")
```

**Result:** No log messages about Sentry when running normally.

### 2. Safe Function Calls

All Sentry helper functions check if Sentry is initialized:

```python
from ai_mem.server.infrastructure.sentry_config import capture_exception

# This is safe to call even without Sentry configured
try:
    risky_operation()
except Exception as e:
    capture_exception(e)  # Does nothing if Sentry not initialized
```

**Functions that are safe to call without Sentry:**
- `capture_exception()` - Silently does nothing
- `capture_message()` - Silently does nothing
- `set_user_context()` - Silently does nothing
- `set_context()` - Silently does nothing

### 3. No Configuration Required

You can run the app without any Sentry configuration:

```bash
# Just start the app - no Sentry setup needed
poetry run uvicorn src.main:app --reload
```

## Configuration Options

### Option 1: Run Without Sentry (Default)

Don't set `SENTRY_DSN` in your `.env` file, or leave it as the placeholder:

```bash
# .env file - Sentry disabled
SENTRY_DSN=http://YOUR_PUBLIC_KEY@localhost:9000/YOUR_PROJECT_ID
```

**Behavior:** App runs normally, no error tracking, no logs about Sentry.

### Option 2: Run With Sentry

Set a valid `SENTRY_DSN` in your `.env` file:

```bash
# .env file - Sentry enabled
SENTRY_DSN=http://abc123@localhost:9000/2
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

**Behavior:** App runs with error tracking, you'll see:
```
INFO - Sentry initialized successfully - Environment: development, Traces: 100.0%, Profiles: 100.0%
```

## Logging Levels

The Sentry integration uses appropriate logging levels:

| Scenario | Log Level | Message | Visible in Production? |
|----------|-----------|---------|----------------------|
| Sentry not configured | `DEBUG` | "Sentry DSN not configured..." | ❌ No |
| Sentry initialized | `INFO` | "Sentry initialized successfully..." | ✅ Yes |

## Best Practices

### Development

You can develop without Sentry:
```bash
# No Sentry configuration needed
poetry run uvicorn src.main:app --reload
```

### Production

For production, configure Sentry for error tracking:
```bash
# Set real Sentry DSN in production .env
SENTRY_DSN=http://your-real-key@localhost:9000/2
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% sampling
```

## Testing

### Test Without Sentry

```bash
# Remove or comment out SENTRY_DSN in .env
# SENTRY_DSN=http://YOUR_PUBLIC_KEY@localhost:9000/YOUR_PROJECT_ID

# Start app
poetry run uvicorn src.main:app --reload

# App runs normally, no Sentry messages
```

### Test With Sentry

```bash
# Set valid SENTRY_DSN in .env
SENTRY_DSN=http://abc123@localhost:9000/2

# Start app
poetry run uvicorn src.main:app --reload

# You'll see: "Sentry initialized successfully..."

# Test error tracking
curl http://localhost:8000/api/v1/ai-mem/test-sentry
```

## Summary

✅ **No configuration required** - App works without Sentry  
✅ **No warnings or errors** - Silent when not configured  
✅ **Safe to use Sentry functions** - All functions check initialization  
✅ **Easy to enable** - Just add DSN to enable error tracking  
✅ **Production-ready** - Appropriate logging levels  

You can safely deploy and run the application without ever setting up Sentry!
