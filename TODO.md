# AI-MEM TODO List

Quick reference for current tasks and priorities.

## 🔥 High Priority (This Week)

### Phase 1: Ingestion Pipeline

- [ ] **Improve Fact Extraction**
  - [ ] Analyze `logs/empty_facts.log` for patterns
  - [ ] Update prompts in `domain/const/prompt.py`
  - [ ] Add examples to prompts
  - [ ] Test with edge cases (greetings, questions, short messages)

- [x] **Implement Memory Storage** ✅ COMPLETE
  - [x] Complete `_create_memory()` method in `MemoryUseCase`
  - [x] Store fact in PostgreSQL
  - [x] Store embedding in pgvector
  - [x] Add metadata (user_id, timestamp, source)
  - [x] Return detailed response with created memories

- [ ] **Add Deduplication**
  - [ ] Search for similar memories before creating
  - [ ] Define similarity threshold
  - [ ] Decide: update existing or create new

- [ ] **Write Tests**
  - [ ] Unit tests for fact extraction
  - [ ] Unit tests for memory creation
  - [ ] Integration test for full pipeline

## 📋 Medium Priority (Next Week)

### Phase 2: Semantic Retrieval

- [ ] **Basic Search Implementation**
  - [ ] Create `SearchUseCase`
  - [ ] Implement vector similarity search
  - [ ] Add search API endpoint: `POST /api/v1/ai-mem/search`
  - [ ] Return top-k similar memories

- [ ] **Search Optimization**
  - [ ] Add vector index (HNSW or IVFFlat)
  - [ ] Benchmark search performance
  - [ ] Add result caching

- [ ] **Filtered Search**
  - [ ] Filter by user_id
  - [ ] Filter by timestamp
  - [ ] Filter by tags

## 🎯 Lower Priority (This Month)

### Phase 3: Logic Engine

- [ ] **Update Logic Design**
  - [ ] Design update vs. create decision flow
  - [ ] Define structured output schemas
  - [ ] Create prompts for LLM reasoning

- [ ] **Memory Merging**
  - [ ] Detect mergeable memories
  - [ ] Implement merge strategy
  - [ ] Test merge quality

- [ ] **Conflict Resolution**
  - [ ] Detect contradictory facts
  - [ ] Implement resolution strategies
  - [ ] Track conflicts

## 🐛 Bugs & Issues

- [ ] None currently

## 💡 Ideas & Improvements

- [ ] Support batch memory creation
- [ ] Add memory export/import
- [ ] Create admin dashboard
- [ ] Add memory analytics
- [ ] Support multiple LLM providers

## ✅ Recently Completed

- [x] Clean Architecture setup
- [x] Dependency Injection implementation
- [x] LLM response parser
- [x] Empty facts logger
- [x] Logging infrastructure
- [x] Database schema
- [x] Basic fact extraction

## 📅 Timeline

### Week 1 (Current)
- Improve fact extraction
- Implement memory storage
- Add deduplication

### Week 2
- Implement basic search
- Add vector index
- Write comprehensive tests

### Week 3-4
- Complete Phase 2 (Retrieval)
- Start Phase 3 (Logic Engine)
- Design update logic

## 🎓 Learning & Research

- [ ] Study mem0 implementation for best practices
- [ ] Research vector index optimization
- [ ] Learn about LLM structured output techniques
- [ ] Explore conflict resolution algorithms

## 📝 Notes

- Check `logs/empty_facts.log` daily for patterns
- Update prompts based on real usage
- Keep tests up to date
- Document design decisions

---

**Last Updated:** 2025-11-22
