# Empty Facts Logger - Simple Guide

## Overview

A dedicated, simple log file that captures **only the raw LLM response** when facts extraction returns empty. No verbose logging, just what you need to debug.

## Log File

**Location:** `logs/empty_facts.log`

**What's Logged:**
- Original user message
- Raw LLM response
- That's it! Clean and simple.

## Example Log Entry

```
2025-11-22 12:09:13 - ================================================================================
2025-11-22 12:09:13 - Original Message: hello
2025-11-22 12:09:13 - LLM Response:
Since the input is not clear or grammatically correct, I will return an empty list.

Output: {"facts" : []}
2025-11-22 12:09:13 - ================================================================================
2025-11-22 12:09:13 - 
```

## Configuration

Add to `.env` (optional, defaults work fine):

```bash
EMPTY_FACTS_LOG_FILE=empty_facts.log
LOG_DIR=logs
```

## Usage

**Automatic!** When facts extraction returns empty, it's automatically logged.

## Viewing the Log

```bash
# View the entire log
cat logs/empty_facts.log

# Follow in real-time
tail -f logs/empty_facts.log

# Count how many times facts were empty
grep -c "Original Message" logs/empty_facts.log

# View last 10 entries
tail -n 50 logs/empty_facts.log
```

## Log Rotation

- **Max size:** 5MB
- **Backups:** 3 files
- **Total:** ~15MB max

Files:
- `empty_facts.log` - Current
- `empty_facts.log.1` - Backup 1
- `empty_facts.log.2` - Backup 2
- `empty_facts.log.3` - Backup 3

## Analyzing Empty Facts

### Step 1: Check the log

```bash
cat logs/empty_facts.log
```

### Step 2: Look for patterns

- Are certain types of messages always empty?
- What does the LLM say in its response?
- Is it a prompt issue or message quality issue?

### Step 3: Improve

Based on what you see:
- Update prompts in `domain/const/prompt.py`
- Handle edge cases (short messages, greetings, etc.)
- Adjust LLM parameters

## Example Analysis

**Log shows:**
```
Original Message: hi
LLM Response: Input is too short, returning empty list.
```

**Action:** Either:
1. Update prompt to handle greetings
2. Add minimum message length validation
3. Return helpful message to user

## Benefits

✅ **Simple** - Only logs what you need  
✅ **Separate file** - Doesn't clutter main logs  
✅ **Easy to analyze** - Clean format  
✅ **Automatic** - No code changes needed  
✅ **Lightweight** - Small file size  

## Main Application Log

The main `ai_mem.log` still logs:
- Application startup/shutdown
- Successful facts extraction
- Errors and exceptions
- General application flow

But **not** the verbose empty facts details - those go to `empty_facts.log`.

## Summary

- **File:** `logs/empty_facts.log`
- **Content:** Original message + raw LLM response
- **When:** Only when facts are empty
- **Why:** Easy debugging without verbose logs

Simple and effective! 🎯
