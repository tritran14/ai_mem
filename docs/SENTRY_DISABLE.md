# Disabling Sentry When Server Is Not Running

If you have Sentry configured but the Sentry server is not running, you can easily disable it to prevent any warnings or connection attempts.

## Quick Solution

### Option 1: Use SENTRY_ENABLED Flag (Recommended)

Set `SENTRY_ENABLED=false` in your `.env` file:

```bash
# .env file
SENTRY_ENABLED=false
SENTRY_DSN=http://abc123@localhost:9000/2
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

**Result:** Sentry is completely disabled, no connection attempts, no warnings.

### Option 2: Comment Out DSN

Comment out the `SENTRY_DSN` line:

```bash
# .env file
# SENTRY_DSN=http://abc123@localhost:9000/2
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

**Result:** Sentry is disabled because DSN is not found.

## Use Cases

### Development Without Sentry Server

```bash
# .env
SENTRY_ENABLED=false  # Disable Sentry
SENTRY_DSN=http://abc123@localhost:9000/2  # Keep DSN for when you need it
```

**When to use:** You have Sentry configured but the Docker containers are not running.

### Development With Sentry Server

```bash
# .env
SENTRY_ENABLED=true  # Enable Sentry
SENTRY_DSN=http://abc123@localhost:9000/2
```

**When to use:** Sentry Docker containers are running (`docker compose up -d` in self-hosted directory).

## What Happens When Sentry Server Is Down?

The integration is designed to handle this gracefully:

### 1. **SDK Logging Suppressed**
```python
# Sentry SDK's own warnings are suppressed
sentry_logger.setLevel(logging.ERROR)
```
- ✅ No warnings about connection failures
- ✅ Only critical SDK errors are logged

### 2. **Graceful Initialization Failure**
```python
try:
    sentry_sdk.init(...)
except Exception as e:
    logger.warning(f"Failed to initialize Sentry: {e}. Continuing without error tracking.")
```
- ✅ App continues to run normally
- ✅ Single warning message, then silent

### 3. **Event Queuing**
- Sentry SDK queues events in memory if server is unreachable
- Events are discarded after shutdown
- No disk writes or persistent errors

## Configuration Summary

| Scenario | SENTRY_ENABLED | SENTRY_DSN | Sentry Server | Behavior |
|----------|----------------|------------|---------------|----------|
| **Disabled** | `false` | Any | Any | ✅ No Sentry, no logs |
| **Not Configured** | Any | Not set | Any | ✅ No Sentry, no logs |
| **Enabled + Server Running** | `true` | Valid | Running | ✅ Full error tracking |
| **Enabled + Server Down** | `true` | Valid | Down | ⚠️ One warning, then silent |

## Best Practice

### For Development

Keep Sentry configured but disabled by default:

```bash
# .env
SENTRY_ENABLED=false  # Default: disabled
SENTRY_DSN=http://abc123@localhost:9000/2
SENTRY_ENVIRONMENT=development
```

**Enable when needed:**
```bash
# When you want to test Sentry
SENTRY_ENABLED=true
```

### For Production

Always enable Sentry in production:

```bash
# .env.production
SENTRY_ENABLED=true
SENTRY_DSN=http://your-production-key@sentry.your-domain.com/2
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% sampling
```

## Testing

### Test with Sentry Disabled

```bash
# Set in .env
SENTRY_ENABLED=false

# Start app
poetry run uvicorn src.main:app --reload

# Expected output: No Sentry messages at all
```

### Test with Sentry Enabled but Server Down

```bash
# Set in .env
SENTRY_ENABLED=true
SENTRY_DSN=http://abc123@localhost:9000/2

# Make sure Sentry server is NOT running
docker compose down  # in self-hosted directory

# Start app
poetry run uvicorn src.main:app --reload

# Expected output: One warning about Sentry initialization failure, then normal operation
```

### Test with Sentry Enabled and Server Running

```bash
# Set in .env
SENTRY_ENABLED=true
SENTRY_DSN=http://abc123@localhost:9000/2

# Start Sentry server
cd ../self-hosted
docker compose up -d

# Start app
poetry run uvicorn src.main:app --reload

# Expected output: "Sentry initialized successfully..."
```

## Summary

✅ **Use `SENTRY_ENABLED=false`** to disable Sentry when server is not running  
✅ **SDK warnings are suppressed** - no noisy logs  
✅ **App continues normally** - no crashes or errors  
✅ **Easy to toggle** - just change one environment variable  
✅ **Production-ready** - graceful handling of all scenarios  

You can now develop without worrying about Sentry server status!
