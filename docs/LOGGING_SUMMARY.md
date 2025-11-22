# Logging Implementation Summary

## 🎯 Problem Solved

**Issue:** When LLM returns empty facts, we need to log detailed information to debug and improve prompts.

**Solution:** Comprehensive logging system with file output and detailed debugging information.

## ✅ What Was Implemented

### 1. Logging Configuration (`infrastructure/logging_config.py`)

**Features:**
- File-based logging with rotation (10MB max, 5 backups)
- Console output for important messages
- Detailed formatting with timestamps, file, and line numbers
- Environment-based configuration

**Usage:**
```python
from ai_mem.server.infrastructure.logging_config import setup_logging

setup_logging()  # Initialize logging
```

### 2. Enhanced MemoryUseCase Logging

**When Facts Are Empty:**
```log
================================================================================
⚠ NO FACTS EXTRACTED - Debug Information:
Original message: hello
System prompt: You are a fact extraction system...
User prompt: Input:
hello
LLM response: Since the input is not clear, returning empty list.
Output: {"facts" : []}
================================================================================
```

**When Facts Are Extracted:**
```log
✓ Extracted 2 facts from message
  Fact 1: User loves programming in Python
  Fact 2: User is learning AI
```

**When Errors Occur:**
```log
================================================================================
❌ ERROR extracting facts: Connection timeout
Message: I love programming
Exception type: TimeoutError
================================================================================
Full traceback:
...
```

### 3. Application Startup Logging

```log
================================================================================
Logging initialized - Level: INFO, File: logs/ai_mem.log
================================================================================
Starting ai-mem application...
Dependency injection container initialized
```

### 4. Environment Configuration

Added to `.env.example`:
```bash
# Logging Configuration
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=ai_mem.log     # Log file name
LOG_DIR=logs            # Directory for log files
```

## 📁 Files Created/Modified

### Created:
1. ✅ `src/ai_mem/server/infrastructure/logging_config.py` - Logging setup
2. ✅ `docs/LOGGING_GUIDE.md` - Complete logging documentation

### Modified:
1. ✅ `src/main.py` - Initialize logging on startup
2. ✅ `src/ai_mem/server/application/use_case/memory.py` - Enhanced logging
3. ✅ `.env.example` - Added logging configuration

## 🚀 Quick Start

### 1. Configure Logging

```bash
# Add to .env
LOG_LEVEL=DEBUG  # For development
LOG_FILE=ai_mem.log
LOG_DIR=logs
```

### 2. Run Application

```bash
poetry run uvicorn src.main:app --reload
```

### 3. Monitor Logs

```bash
# Real-time monitoring
tail -f logs/ai_mem.log

# Filter for empty facts
tail -f logs/ai_mem.log | grep "NO FACTS"

# Filter for errors
tail -f logs/ai_mem.log | grep "ERROR"
```

## 📊 Log Levels

| Level | Use Case | What Gets Logged |
|-------|----------|------------------|
| `DEBUG` | Development | Everything (very verbose) |
| `INFO` | Production | Important events |
| `WARNING` | Production | Empty facts, potential issues |
| `ERROR` | Production | Errors, exceptions |

## 🔍 Debugging Empty Facts

### Step 1: Check Logs

```bash
grep -A 10 "NO FACTS EXTRACTED" logs/ai_mem.log
```

### Step 2: Analyze Pattern

Look at the logged information:
- **Original message**: Is it clear enough?
- **System prompt**: Is it appropriate?
- **LLM response**: Why did it return empty?

### Step 3: Improve

Based on analysis:
1. Update prompts in `domain/const/prompt.py`
2. Adjust LLM parameters
3. Add examples to prompts

## 📝 Example Log Output

### Empty Facts Case

```log
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:75] - Extracting facts from message: hello...
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:76] - System prompt: You are a fact extraction system...
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:83] - LLM raw response: Since the input is not clear or grammatically correct, I will return an empty list.

Output: {"facts" : []}
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:87] - ================================================================================
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:88] - ⚠ NO FACTS EXTRACTED - Debug Information:
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:89] - Original message: hello
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:90] - System prompt: You are a fact extraction system...
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:91] - User prompt: Input:
hello
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:92] - LLM response: Since the input is not clear or grammatically correct, I will return an empty list.

Output: {"facts" : []}
2025-11-22 12:01:37 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:93] - ================================================================================
```

### Successful Extraction

```log
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:75] - Extracting facts from message: I love programming in Python and learning AI...
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:83] - LLM raw response: {"facts": ["User loves programming in Python", "User is learning AI"]}
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - INFO - [memory.py:88] - ✓ Extracted 2 facts from message
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:90] -   Fact 1: User loves programming in Python
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:90] -   Fact 2: User is learning AI
```

## 🛠️ Log Analysis Commands

```bash
# Count empty facts cases
grep -c "NO FACTS EXTRACTED" logs/ai_mem.log

# Find all errors
grep "ERROR" logs/ai_mem.log

# Get last 100 lines
tail -n 100 logs/ai_mem.log

# Search with context
grep -A 5 -B 5 "NO FACTS" logs/ai_mem.log

# Search in all log files
grep "NO FACTS" logs/ai_mem.log*
```

## 📈 Benefits

✅ **Debug empty facts** - See exactly why LLM returned empty  
✅ **Improve prompts** - Analyze patterns and optimize  
✅ **Track errors** - Full exception tracebacks  
✅ **Monitor production** - File-based logs with rotation  
✅ **Easy analysis** - Structured, searchable logs  

## 🎓 Best Practices

### Development
```bash
LOG_LEVEL=DEBUG  # See everything
```

### Production
```bash
LOG_LEVEL=INFO   # Important events only
```

### Monitoring
```bash
# Daily check
grep "WARNING\|ERROR" logs/ai_mem.log | tail -n 50

# Count issues
echo "Empty facts: $(grep -c 'NO FACTS' logs/ai_mem.log)"
echo "Errors: $(grep -c 'ERROR' logs/ai_mem.log)"
```

## 📚 Documentation

- **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)** - Complete logging guide
- **[QUICK_START.md](QUICK_START.md)** - Setup guide
- **[LLM_RESPONSE_PARSER.md](LLM_RESPONSE_PARSER.md)** - Parser documentation

## 🎉 Summary

You now have:
- ✅ Comprehensive logging system
- ✅ Detailed empty facts debugging
- ✅ File-based logs with rotation
- ✅ Environment configuration
- ✅ Easy log analysis tools

**Next Steps:**
1. Set `LOG_LEVEL=DEBUG` in `.env`
2. Run the application
3. Check `logs/ai_mem.log` for empty facts cases
4. Analyze patterns and improve prompts!

**Log File Location:** `logs/ai_mem.log`

Happy debugging! 🚀
