# Dependency Injection Best Practices - Where to Use @inject

## The Question

**Should we use `@inject` decorator in services and use cases, or only in interface adapters?**

## TL;DR - Best Practice ✅

**Use `@inject` ONLY in Interface Adapters (entry points)**
- REST API routes
- CLI commands
- GraphQL resolvers
- Background job handlers

**Use Constructor Injection everywhere else**
- Use Cases
- Services
- Repositories

## Why This Matters

### 1. **Clean Architecture Principle**

```
┌─────────────────────────────────────────┐
│   Interface Adapters (Entry Points)    │  ← @inject HERE
│   - REST routes                         │
│   - CLI commands                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Application Layer (Use Cases)        │  ← Constructor Injection
│   - Business logic                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Infrastructure (Services)             │  ← Constructor Injection
│   - External services                   │
└─────────────────────────────────────────┘
```

### 2. **Dependency Flow**

```python
# ✅ CORRECT FLOW
HTTP Request 
  → Router (@inject) 
    → Use Case (constructor injection) 
      → Service (constructor injection)

# ❌ WRONG FLOW
HTTP Request 
  → Router (@inject) 
    → Use Case (@inject) 
      → Service (@inject)
```

## Detailed Comparison

### Approach 1: @inject Everywhere ❌

```python
# Container
class Container(containers.DeclarativeContainer):
    config = providers.Singleton(AppConfig.from_env)
    llm_service = providers.Singleton(OllamaService)
    vector_store = providers.Singleton(PgVectorStore)
    memory_use_case = providers.Singleton(MemoryUseCase)
    
    wiring_config = containers.WiringConfiguration(
        modules=["ai_mem.server"]  # Wire everything
    )

# Service with @inject
class OllamaService(LlmInterface):
    @inject
    def __init__(
        self,
        model: str = Provide[Container.config.provided.llm.model],
        host: str = Provide[Container.config.provided.llm.host],
    ):
        self.model = model
        self._client = Client(host=host)

# Use Case with @inject
class MemoryUseCase:
    @inject
    def __init__(
        self,
        llm_service: LlmInterface = Provide[Container.llm_service],
        vector_store: BaseVectorStore = Provide[Container.vector_store],
    ):
        self.llm_service = llm_service
        self.vector_store = vector_store

# Router with @inject
@router.post("/")
@inject
def create_memory(
    request: CreateMemoryRequest,
    memory_use_case: MemoryUseCase = Depends(Provide[Container.memory_use_case]),
):
    memory_use_case.add(request)
```

**Problems:**
- ❌ Tight coupling to DI framework throughout codebase
- ❌ Hard to test (need container for everything)
- ❌ Violates Clean Architecture (inner layers depend on outer)
- ❌ Slower startup (wires all modules)
- ❌ Less explicit about dependencies

### Approach 2: @inject Only at Entry Points ✅

```python
# Container
class Container(containers.DeclarativeContainer):
    config = providers.Singleton(AppConfig.from_env)
    
    llm_service = providers.Singleton(
        OllamaService,
        model=config.provided.llm.model,
        host=config.provided.llm.host,
    )
    
    vector_store = providers.Singleton(
        PgVectorStore,
        connection_string=config.provided.database.connection_string,
    )
    
    memory_use_case = providers.Factory(
        MemoryUseCase,
        llm_service=llm_service,
        vector_store=vector_store,
    )
    
    wiring_config = containers.WiringConfiguration(
        modules=[
            "ai_mem.server.interface_adapter.rest.router",  # Only entry points
        ]
    )

# Service with constructor injection (NO @inject)
class OllamaService(LlmInterface):
    def __init__(self, model: str, host: str):
        self.model = model
        self._client = Client(host=host)

# Use Case with constructor injection (NO @inject)
class MemoryUseCase:
    def __init__(
        self,
        llm_service: LlmInterface,
        vector_store: BaseVectorStore,
    ):
        self.llm_service = llm_service
        self.vector_store = vector_store

# Router with @inject (ONLY entry point)
@router.post("/")
@inject
def create_memory(
    request: CreateMemoryRequest,
    memory_use_case: MemoryUseCase = Depends(Provide[Container.memory_use_case]),
):
    memory_use_case.add(request)
```

**Benefits:**
- ✅ Clean Architecture compliant
- ✅ Easy to test (no DI framework needed for unit tests)
- ✅ Faster startup (only wires entry points)
- ✅ Explicit dependencies
- ✅ Framework-agnostic inner layers

## Testing Comparison

### With @inject Everywhere ❌

```python
# Need container even for simple tests
def test_memory_use_case():
    container = Container()
    container.wire(modules=["tests"])
    
    # Complex setup
    use_case = container.memory_use_case()
    
    # Test
    use_case.add(request)
```

### With Constructor Injection ✅

```python
# Simple, clean tests
def test_memory_use_case():
    # Create mocks
    mock_llm = MockLlmService()
    mock_vector = MockVectorStore()
    
    # Direct instantiation
    use_case = MemoryUseCase(
        llm_service=mock_llm,
        vector_store=mock_vector
    )
    
    # Test
    use_case.add(request)
```

## Wiring Configuration Best Practices

### ❌ Bad: Wire Everything

```python
wiring_config = containers.WiringConfiguration(
    modules=["ai_mem.server"]  # Too broad!
)
```

**Problems:**
- Scans all modules unnecessarily
- Slower startup
- Unclear which modules use DI
- May wire modules that don't need it

### ✅ Good: Wire Only Entry Points

```python
wiring_config = containers.WiringConfiguration(
    modules=[
        # Only modules with @inject decorator
        "ai_mem.server.interface_adapter.rest.router",
        "ai_mem.server.interface_adapter.rest.admin_router",
        "ai_mem.server.interface_adapter.cli.commands",
    ]
)
```

**Benefits:**
- Fast startup
- Explicit about DI usage
- Easy to debug
- Clear separation

## When to Add New Modules to Wiring

### Add to Wiring When:
✅ Creating new REST API routes  
✅ Adding CLI commands  
✅ Adding GraphQL resolvers  
✅ Adding background job handlers  

### DON'T Add to Wiring When:
❌ Creating new use cases  
❌ Adding new services  
❌ Creating repositories  
❌ Adding domain entities  

## Real-World Example

### Scenario: Adding a Search Feature

```python
# 1. Create interface (NO @inject)
class SearchServiceInterface(ABC):
    @abstractmethod
    def search(self, query: str) -> list:
        pass

# 2. Implement service (NO @inject)
class ElasticsearchService(SearchServiceInterface):
    def __init__(self, host: str, index: str):
        self.host = host
        self.index = index
        self.client = Elasticsearch(host)
    
    def search(self, query: str) -> list:
        return self.client.search(index=self.index, query=query)

# 3. Create use case (NO @inject)
class SearchUseCase:
    def __init__(
        self,
        search_service: SearchServiceInterface,
        memory_service: MemoryServiceInterface,
    ):
        self.search_service = search_service
        self.memory_service = memory_service
    
    def execute(self, query: str):
        results = self.search_service.search(query)
        return self.memory_service.enrich(results)

# 4. Register in container
class Container(containers.DeclarativeContainer):
    # ... existing providers ...
    
    search_service = providers.Singleton(
        ElasticsearchService,
        host=config.provided.elasticsearch.host,
        index=config.provided.elasticsearch.index,
    )
    
    search_use_case = providers.Factory(
        SearchUseCase,
        search_service=search_service,
        memory_service=memory_service,
    )

# 5. Use in router (@inject ONLY here)
@router.get("/search")
@inject
def search(
    query: str,
    search_use_case: SearchUseCase = Depends(Provide[Container.search_use_case]),
):
    results = search_use_case.execute(query)
    return {"results": results}

# 6. NO need to update wiring config!
# Already wiring "ai_mem.server.interface_adapter.rest.router"
```

## Summary Table

| Layer | Use @inject? | Wiring Needed? | Injection Method |
|-------|--------------|----------------|------------------|
| **Interface Adapters** | ✅ YES | ✅ YES | `@inject` + `Depends(Provide[...])` |
| **Use Cases** | ❌ NO | ❌ NO | Constructor parameters |
| **Services** | ❌ NO | ❌ NO | Constructor parameters |
| **Repositories** | ❌ NO | ❌ NO | Constructor parameters |
| **Domain Entities** | ❌ NO | ❌ NO | No DI at all |

## Key Takeaways

1. **@inject is for entry points only** - REST routes, CLI, etc.
2. **Constructor injection everywhere else** - Use cases, services
3. **Wire only modules with @inject** - Be explicit, not broad
4. **Keep inner layers pure** - No framework dependencies
5. **Container manages the graph** - Providers handle dependency resolution

## Your Question Answered

> "Should we @inject into vector_store and llm_service, memory_use_case instead of manually adding into container?"

**Answer: NO** ❌

**Correct approach:**
- Define dependencies in container with providers
- Use constructor injection in services and use cases
- Use `@inject` only in interface adapters (routers)
- Wire only the interface adapter modules

This keeps your architecture clean, testable, and maintainable!

## Further Reading

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Dependency Injection Principles](https://python-dependency-injector.ets-labs.org/introduction/di_in_python.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
