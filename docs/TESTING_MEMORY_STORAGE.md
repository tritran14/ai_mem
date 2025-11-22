# Testing Memory Storage

## Quick Test Guide

### 1. Start the Application

```bash
# Make sure PostgreSQL and Ollama are running
docker-compose up -d  # If using Docker

# Start the application
poetry run uvicorn src.main:app --reload
```

### 2. Test Memory Creation

#### Using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/ai-mem/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "text": "I love programming in Python and I am learning AI",
    "metadata": {}
  }'
```

#### Expected Response:

```json
{
  "success": true,
  "message": "Created 2 memories",
  "facts_count": 2,
  "created_count": 2,
  "failed_count": 0,
  "memories": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "fact": "User loves programming in Python"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "fact": "User is learning AI"
    }
  ],
  "failures": null
}
```

### 3. Test with Empty Facts

```bash
curl -X POST "http://localhost:8000/api/v1/ai-mem/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "text": "hello",
    "metadata": {}
  }'
```

#### Expected Response:

```json
{
  "success": false,
  "message": "No facts extracted",
  "facts_count": 0
}
```

**Check:** `logs/empty_facts.log` will have the LLM response

### 4. Check the Database

```bash
# Connect to PostgreSQL
psql -h localhost -p 5440 -U ai_mem_user -d ai_mem

# View stored memories
SELECT id, payload->>'fact' as fact, payload->>'user_id' as user_id 
FROM temp_memory 
ORDER BY payload->>'created_at' DESC 
LIMIT 10;
```

### 5. Monitor Logs

```bash
# Watch main log
tail -f logs/ai_mem.log

# Watch empty facts log
tail -f logs/empty_facts.log
```

## What Gets Stored

For each fact, the following is stored in pgvector:

- **ID**: Unique UUID for the memory
- **Vector**: Embedding of the fact (from Ollama)
- **Payload** (JSON):
  - `user_id`: User who created the memory
  - `original_message`: The original input message
  - `fact`: The extracted fact text
  - `created_at`: ISO timestamp
  - `data`: The fact text (for retrieval)
  - Any additional metadata from request

## Example Storage

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "vector": [0.123, 0.456, ...],  // 2048-dimensional vector
  "payload": {
    "user_id": "test-user-123",
    "original_message": "I love programming in Python",
    "fact": "User loves programming in Python",
    "created_at": "2025-11-22T12:29:19.123456",
    "data": "User loves programming in Python"
  }
}
```

## Testing Different Scenarios

### Scenario 1: Multiple Facts

```bash
curl -X POST "http://localhost:8000/api/v1/ai-mem/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-456",
    "text": "My name is John. I work as a software engineer at Google. I enjoy hiking on weekends.",
    "metadata": {"source": "conversation"}
  }'
```

Expected: 3 facts extracted and stored

### Scenario 2: Short Message

```bash
curl -X POST "http://localhost:8000/api/v1/ai-mem/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-789",
    "text": "hi",
    "metadata": {}
  }'
```

Expected: No facts extracted, logged to `empty_facts.log`

### Scenario 3: Question

```bash
curl -X POST "http://localhost:8000/api/v1/ai-mem/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-789",
    "text": "What is the weather today?",
    "metadata": {}
  }'
```

Expected: Likely no facts (questions don't contain facts about the user)

## Verification Checklist

- [ ] Facts are extracted from message
- [ ] Embeddings are generated
- [ ] Memories are stored in database
- [ ] Unique IDs are generated
- [ ] Metadata is included
- [ ] Timestamps are added
- [ ] Response includes created memories
- [ ] Empty facts are logged separately
- [ ] Errors are handled gracefully

## Common Issues

### Issue: No facts extracted
**Check:** `logs/empty_facts.log` for LLM response  
**Action:** Improve prompts in `domain/const/prompt.py`

### Issue: Database connection error
**Check:** PostgreSQL is running  
**Action:** `docker-compose up -d` or check connection string

### Issue: Ollama error
**Check:** Ollama is running  
**Action:** `ollama serve` or check `OLLAMA_HOST` in `.env`

### Issue: Embedding dimension mismatch
**Check:** Vector column dimension in database  
**Action:** Ensure pgvector column matches embedding dimension

## Next Steps

After verifying storage works:

1. **Implement Search** - Query stored memories
2. **Add Deduplication** - Check for existing similar memories
3. **Implement Update Logic** - Update existing memories instead of creating duplicates

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with Swagger UI.
