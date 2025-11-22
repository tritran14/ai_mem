# Sentry Integration - Quick Start

## ⚡ Quick Setup (5 minutes)

### 1. Create Sentry Project
```bash
# Open Sentry in browser
open http://localhost:9000

# Login: tranvantri2000@gmail.com
# Create new Python/FastAPI project named "ai-mem"
# Copy the DSN (looks like: http://abc123@localhost:9000/2)
```

### 2. Configure Environment
```bash
# Edit .env file
nano .env

# Add your DSN:
SENTRY_DSN=http://YOUR_KEY@localhost:9000/YOUR_PROJECT_ID
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

### 3. Test Integration
```bash
# Start your app
poetry run uvicorn src.main:app --reload

# Test Sentry (in another terminal)
curl http://localhost:8000/api/v1/ai-mem/test-sentry

# Check Sentry dashboard
open http://localhost:9000
```

## 📊 What You Get

✅ **Automatic Error Tracking** - All unhandled exceptions captured  
✅ **Performance Monitoring** - API endpoint response times  
✅ **Log Integration** - ERROR-level logs sent to Sentry  
✅ **User Context** - Track which users experience errors  
✅ **Custom Context** - Add database queries, API calls, etc.

## 🔧 Common Usage

### Capture Exceptions
```python
from ai_mem.server.infrastructure.sentry_config import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(e, operation="risky_op", user_id="123")
```

### Capture Messages
```python
from ai_mem.server.infrastructure.sentry_config import capture_message

capture_message("Important event occurred", level="warning", user_id="123")
```

### Set User Context
```python
from ai_mem.server.infrastructure.sentry_config import set_user_context

set_user_context(user_id="123", email="user@example.com")
```

## 📝 Files Modified

- ✅ `pyproject.toml` - Added sentry-sdk dependency
- ✅ `.env.example` - Added Sentry configuration
- ✅ `src/main.py` - Initialized Sentry on startup
- ✅ `src/ai_mem/server/infrastructure/sentry_config.py` - Sentry configuration module
- ✅ `src/ai_mem/server/interface_adapter/rest/router.py` - Added test endpoint
- ✅ `docs/SENTRY_SETUP.md` - Complete documentation

## 🎯 Next Steps

1. **Get your DSN** from Sentry dashboard
2. **Update .env** with your actual DSN
3. **Restart your app** to apply changes
4. **Test the integration** using the test endpoint
5. **Check Sentry dashboard** to see captured events

## 📚 Full Documentation

See `docs/SENTRY_SETUP.md` for complete documentation including:
- Detailed setup instructions
- Advanced usage examples
- Best practices
- Troubleshooting guide
