# Sentry Auto-Detection

The ai-mem application **automatically detects** if Sentry server is available and only initializes error tracking when the server is reachable.

## How It Works

### Automatic Connection Testing

When your app starts, it:

1. **Checks if DSN is configured** - Skips if not set or placeholder
2. **Tests connection to Sentry server** - Quick 3-second socket test
3. **Initializes Sentry** - Only if server is reachable
4. **Continues normally** - If server is down, app runs without error tracking

### No Configuration Needed!

You don't need to manually enable/disable Sentry. Just configure the DSN and the app handles the rest:

```bash
# .env file
SENTRY_DSN=http://abc123@localhost:9000/2
SENTRY_ENVIRONMENT=development
```

**That's it!** The app will:
- ✅ Use Sentry if server is running
- ✅ Skip Sentry if server is not running
- ✅ No warnings or errors either way

## Behavior Examples

### Scenario 1: Sentry Server Running

```bash
# Sentry Docker containers are running
cd self-hosted
docker compose up -d

# Start your app
cd ../ai_mem
poetry run uvicorn src.main:app --reload
```

**Logs:**
```
INFO - Starting ai-mem application...
DEBUG - Testing connection to Sentry server...
INFO - Sentry initialized successfully - Environment: development, Traces: 100.0%, Profiles: 100.0%
INFO - Dependency injection container initialized
```

**Result:** ✅ Full error tracking enabled

### Scenario 2: Sentry Server Not Running

```bash
# Sentry Docker containers are NOT running
cd self-hosted
docker compose down

# Start your app
cd ../ai_mem
poetry run uvicorn src.main:app --reload
```

**Logs:**
```
INFO - Starting ai-mem application...
DEBUG - Testing connection to Sentry server...
INFO - Sentry server is not available, running without error tracking
INFO - Dependency injection container initialized
```

**Result:** ✅ App runs normally without Sentry

### Scenario 3: DSN Not Configured

```bash
# .env file
SENTRY_DSN=http://YOUR_PUBLIC_KEY@localhost:9000/YOUR_PROJECT_ID

# Start your app
poetry run uvicorn src.main:app --reload
```

**Logs:**
```
INFO - Starting ai-mem application...
DEBUG - Sentry DSN not configured, running without error tracking
INFO - Dependency injection container initialized
```

**Result:** ✅ App runs normally without Sentry

## Connection Test Details

### What Gets Tested

The connection test:
- ✅ Parses the DSN to extract host and port
- ✅ Attempts a TCP socket connection
- ✅ Times out after 3 seconds
- ✅ Returns true/false based on connectivity

### Fast and Lightweight

```python
def _test_sentry_connection(dsn: str, timeout: int = 3) -> bool:
    # Quick socket connection test
    # No HTTP requests, no authentication
    # Just checks if server is listening
```

**Performance:**
- ⚡ ~10ms if server is running
- ⚡ ~3 seconds if server is down (timeout)
- ⚡ No impact on app startup when server is available

## Log Levels

| Scenario | Log Level | Message |
|----------|-----------|---------|
| DSN not configured | `DEBUG` | "Sentry DSN not configured..." |
| Testing connection | `DEBUG` | "Testing connection to Sentry server..." |
| Server not available | `INFO` | "Sentry server is not available..." |
| Sentry initialized | `INFO` | "Sentry initialized successfully..." |
| Initialization failed | `WARNING` | "Failed to initialize Sentry..." |

## Development Workflow

### Normal Development (No Sentry)

```bash
# Just start your app - no Sentry setup needed
poetry run uvicorn src.main:app --reload
```

**Result:** App starts quickly, no Sentry messages (except DEBUG level)

### Development with Sentry

```bash
# Start Sentry server
cd self-hosted
docker compose up -d

# Start your app
cd ../ai_mem
poetry run uvicorn src.main:app --reload
```

**Result:** App starts with Sentry enabled, errors are tracked

### Switching Between Modes

**No action needed!** Just start/stop the Sentry Docker containers:

```bash
# Enable Sentry
cd self-hosted && docker compose up -d

# Disable Sentry
cd self-hosted && docker compose down
```

Your app automatically adapts on next restart.

## Production Deployment

### Recommended Setup

1. **Configure DSN** in production environment:
   ```bash
   SENTRY_DSN=http://your-key@sentry.your-domain.com/2
   SENTRY_ENVIRONMENT=production
   SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% sampling
   ```

2. **Ensure Sentry server is running**:
   ```bash
   docker compose up -d
   ```

3. **Deploy your app** - It will automatically connect to Sentry

### Failover Behavior

If Sentry server goes down in production:
- ✅ App continues to run normally
- ✅ No errors or crashes
- ✅ Single INFO log: "Sentry server is not available..."
- ✅ Errors are not tracked until Sentry is back

## Benefits

✅ **Zero configuration** - Just set DSN, everything else is automatic  
✅ **Intelligent detection** - Knows when Sentry is available  
✅ **No manual toggling** - No need to enable/disable  
✅ **Fast startup** - Quick connection test (10ms when available)  
✅ **Graceful degradation** - App works with or without Sentry  
✅ **Clean logs** - Appropriate log levels for each scenario  
✅ **Developer-friendly** - Works seamlessly in all environments  

## Summary

The Sentry integration is now **fully automatic**:

1. Configure your DSN once
2. Start/stop Sentry server as needed
3. Your app automatically adapts
4. No manual configuration required

**It just works!** 🎉
