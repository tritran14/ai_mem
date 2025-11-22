# Logging Configuration Guide

## Overview

The ai-mem application now includes comprehensive logging to help debug issues, especially when LLM fact extraction returns empty results.

## Features

✅ **File-based logging** - All logs saved to rotating log files  
✅ **Console output** - Important logs shown in terminal  
✅ **Detailed debugging** - Full context when facts extraction fails  
✅ **Log rotation** - Automatic file rotation (10MB max, 5 backups)  
✅ **Environment configuration** - Customize via .env file  

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Logging Configuration
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=ai_mem.log     # Log file name
LOG_DIR=logs            # Directory for log files
```

### Log Levels

| Level | When to Use | What Gets Logged |
|-------|-------------|------------------|
| `DEBUG` | Development, troubleshooting | Everything (very verbose) |
| `INFO` | Production (default) | Important events, facts extracted |
| `WARNING` | Production | Empty facts, potential issues |
| `ERROR` | Production | Errors, exceptions |
| `CRITICAL` | Production | Critical failures |

**Recommendation:** Use `INFO` for production, `DEBUG` for development.

## Log File Structure

### Location

```
ai_mem/
├── logs/                    # Log directory
│   ├── ai_mem.log          # Current log file
│   ├── ai_mem.log.1        # Backup 1 (most recent)
│   ├── ai_mem.log.2        # Backup 2
│   ├── ai_mem.log.3        # Backup 3
│   ├── ai_mem.log.4        # Backup 4
│   └── ai_mem.log.5        # Backup 5 (oldest)
```

### Rotation

- **Max file size:** 10MB
- **Backup count:** 5 files
- **Total storage:** ~50MB max

When `ai_mem.log` reaches 10MB:
1. `ai_mem.log` → `ai_mem.log.1`
2. `ai_mem.log.1` → `ai_mem.log.2`
3. ... and so on
4. `ai_mem.log.5` is deleted
5. New `ai_mem.log` is created

## Log Format

### File Logs (Detailed)

```
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:85] - ⚠ NO FACTS EXTRACTED - Debug Information:
```

Format: `timestamp - logger_name - level - [file:line] - message`

### Console Logs (Simple)

```
2025-11-22 12:01:36 - WARNING - ⚠ NO FACTS EXTRACTED - Debug Information:
```

Format: `timestamp - level - message`

## Empty Facts Logging

### What Gets Logged

When fact extraction returns empty results, the following is logged:

```
================================================================================
⚠ NO FACTS EXTRACTED - Debug Information:
Original message: <the user's input message>
System prompt: <the system prompt used>
User prompt: <the user prompt used>
LLM response: <the raw LLM response>
================================================================================
```

### Example Log Entry

```log
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:85] - ================================================================================
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:86] - ⚠ NO FACTS EXTRACTED - Debug Information:
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:87] - Original message: hello
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:88] - System prompt: You are a fact extraction system...
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:89] - User prompt: Input:
hello
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:90] - LLM response: Since the input is not clear or grammatically correct, I will return an empty list.

Output: {"facts" : []}
2025-11-22 12:01:36 - ai_mem.server.application.use_case.memory - WARNING - [memory.py:91] - ================================================================================
```

## Successful Facts Extraction

When facts are successfully extracted:

```log
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - INFO - [memory.py:84] - ✓ Extracted 2 facts from message
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:86] -   Fact 1: User loves programming in Python
2025-11-22 12:05:42 - ai_mem.server.application.use_case.memory - DEBUG - [memory.py:86] -   Fact 2: User is learning AI
```

## Error Logging

When an exception occurs:

```log
================================================================================
❌ ERROR extracting facts: Connection timeout
Message: I love programming
Exception type: TimeoutError
================================================================================
Full traceback:
Traceback (most recent call last):
  File "memory.py", line 75, in _get_facts
    response = self.llm_service.generate_response(...)
  ...
```

## Viewing Logs

### Real-time Monitoring

```bash
# Follow the log file in real-time
tail -f logs/ai_mem.log

# Filter for warnings only
tail -f logs/ai_mem.log | grep WARNING

# Filter for empty facts
tail -f logs/ai_mem.log | grep "NO FACTS"
```

### Search Logs

```bash
# Find all empty facts cases
grep "NO FACTS EXTRACTED" logs/ai_mem.log

# Find all errors
grep "ERROR" logs/ai_mem.log

# Find specific message
grep "hello" logs/ai_mem.log

# Count empty facts occurrences
grep -c "NO FACTS EXTRACTED" logs/ai_mem.log
```

### Analyze Logs

```bash
# Get last 100 lines
tail -n 100 logs/ai_mem.log

# Get lines with context (5 lines before and after)
grep -A 5 -B 5 "NO FACTS" logs/ai_mem.log

# Search in all backup logs
grep "NO FACTS" logs/ai_mem.log*
```

## Debugging Empty Facts

### Step 1: Check the Logs

```bash
# Find empty facts cases
grep -A 10 "NO FACTS EXTRACTED" logs/ai_mem.log
```

### Step 2: Analyze the Pattern

Look for:
- **Original message**: Is it too vague? Too short?
- **System prompt**: Is it clear enough?
- **LLM response**: What did the LLM say?

### Step 3: Improve Prompts

Based on log analysis, you can:
1. Improve the system prompt in `domain/const/prompt.py`
2. Add examples to the prompt
3. Adjust the LLM model or parameters

### Example Analysis

**Log shows:**
```
Original message: hi
LLM response: Input is too short, returning empty list.
```

**Action:** Update prompt to handle greetings or require minimum message length.

## Log Levels in Code

### DEBUG - Development Details

```python
logger.debug(f"Extracting facts from message: {message[:100]}...")
logger.debug(f"System prompt: {system_prompt[:200]}...")
logger.debug(f"LLM raw response: {response}")
```

**When:** Detailed debugging information

### INFO - Important Events

```python
logger.info(f"✓ Extracted {len(facts)} facts from message")
logger.info("Starting ai-mem application...")
```

**When:** Normal operation, successful events

### WARNING - Potential Issues

```python
logger.warning("⚠ NO FACTS EXTRACTED - Debug Information:")
logger.warning(f"Original message: {message}")
```

**When:** Something unexpected but not an error

### ERROR - Errors

```python
logger.error(f"❌ ERROR extracting facts: {e}")
logger.exception("Full traceback:")
```

**When:** Exceptions, failures

## Best Practices

### 1. Set Appropriate Log Level

```bash
# Development
LOG_LEVEL=DEBUG

# Production
LOG_LEVEL=INFO
```

### 2. Monitor Logs Regularly

```bash
# Check for issues daily
grep "WARNING\|ERROR" logs/ai_mem.log | tail -n 50
```

### 3. Archive Old Logs

```bash
# Compress old logs
gzip logs/ai_mem.log.5

# Move to archive
mv logs/ai_mem.log.*.gz archive/
```

### 4. Use Log Aggregation (Production)

For production, consider:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

## Troubleshooting

### Logs Not Appearing

**Check:**
1. `LOG_DIR` exists and is writable
2. `LOG_LEVEL` is set correctly
3. Application has file write permissions

**Solution:**
```bash
# Create logs directory
mkdir -p logs

# Check permissions
ls -la logs/

# Set permissions if needed
chmod 755 logs/
```

### Too Many Logs

**Solution:**
```bash
# Increase log level
LOG_LEVEL=WARNING  # Only warnings and errors

# Reduce rotation size
# Edit logging_config.py: maxBytes=5*1024*1024  # 5MB
```

### Can't Find Specific Logs

**Solution:**
```bash
# Search all log files
grep -r "search term" logs/

# Use more specific search
grep -E "pattern1|pattern2" logs/ai_mem.log
```

## Integration with Monitoring

### Example: Alert on Empty Facts

```bash
#!/bin/bash
# monitor_empty_facts.sh

COUNT=$(grep -c "NO FACTS EXTRACTED" logs/ai_mem.log)

if [ $COUNT -gt 10 ]; then
    echo "Alert: $COUNT empty facts cases found!"
    # Send notification (email, Slack, etc.)
fi
```

### Example: Daily Report

```bash
#!/bin/bash
# daily_report.sh

echo "=== Daily Log Report ==="
echo "Empty facts: $(grep -c 'NO FACTS' logs/ai_mem.log)"
echo "Errors: $(grep -c 'ERROR' logs/ai_mem.log)"
echo "Total requests: $(grep -c 'Extracting facts' logs/ai_mem.log)"
```

## Summary

✅ **Comprehensive logging** for debugging  
✅ **Detailed empty facts logging** with full context  
✅ **File rotation** to manage disk space  
✅ **Environment configuration** for flexibility  
✅ **Easy log analysis** with grep and tail  

**Key Files:**
- `logs/ai_mem.log` - Current log file
- `.env` - Logging configuration
- `infrastructure/logging_config.py` - Logging setup

**Next Steps:**
1. Set `LOG_LEVEL=DEBUG` in `.env` for development
2. Monitor `logs/ai_mem.log` for empty facts cases
3. Analyze patterns and improve prompts
4. Switch to `LOG_LEVEL=INFO` for production
