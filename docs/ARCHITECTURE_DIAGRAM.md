# Clean Architecture Layers - Dependency Flow

This document visualizes the dependency flow in the ai-mem project following Clean Architecture principles.

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAIN.PY (Entry Point)                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Container Initialization                   │    │
│  │  - Load Configuration                                   │    │
│  │  - Wire Dependencies                                    │    │
│  │  - Manage Lifecycle                                     │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              INTERFACE ADAPTERS (Outer Layer)                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    REST API Router                      │    │
│  │                                                         │    │
│  │  @router.post("/")                                     │    │
│  │  @inject                                               │    │
│  │  def create_memory(                                    │    │
│  │      memory_use_case: MemoryUseCase = Depends(...)    │    │
│  │  )                                                     │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER (Use Cases)                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                   MemoryUseCase                        │    │
│  │                                                         │    │
│  │  def __init__(                                         │    │
│  │      llm_service: LlmInterface,                       │    │
│  │      vector_store: BaseVectorStore                    │    │
│  │  )                                                     │    │
│  │                                                         │    │
│  │  def add(request):                                     │    │
│  │      facts = self.llm_service.generate_response()     │    │
│  │      embeddings = self.llm_service.embed()            │    │
│  │      self.vector_store.insert()                       │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ depends on (abstractions)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER (Interfaces)                     │
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   LlmInterface       │      │  BaseVectorStore     │        │
│  │                      │      │                      │        │
│  │  + embed()          │      │  + insert()          │        │
│  │  + generate_response()│    │                      │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ implemented by
                              │
┌─────────────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER (Implementations)              │
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   OllamaService      │      │   PgVectorStore      │        │
│  │                      │      │                      │        │
│  │  implements          │      │  implements          │        │
│  │  LlmInterface        │      │  BaseVectorStore     │        │
│  │                      │      │                      │        │
│  │  + embed()          │      │  + insert()          │        │
│  │  + generate_response()│    │                      │        │
│  └──────────────────────┘      └──────────────────────┘        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Configuration (config.py)                  │    │
│  │  - DatabaseConfig                                      │    │
│  │  - LLMConfig                                           │    │
│  │  - VectorStoreConfig                                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │          DI Container (container.py)                    │    │
│  │                                                         │    │
│  │  config = Singleton(AppConfig.from_env)               │    │
│  │  llm_service = Singleton(OllamaService, ...)          │    │
│  │  vector_store = Singleton(PgVectorStore, ...)         │    │
│  │  memory_use_case = Factory(MemoryUseCase, ...)        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Dependency Rules

### ✅ Allowed Dependencies (Inward)
- Interface Adapters → Application Layer
- Application Layer → Domain Layer
- Infrastructure → Domain Layer
- Infrastructure → Application Layer (for implementation)

### ❌ Forbidden Dependencies (Outward)
- Domain Layer → Application Layer
- Domain Layer → Infrastructure Layer
- Application Layer → Infrastructure Layer (direct)

## Dependency Injection Flow

```
1. Application Startup
   ├── Load .env file
   ├── Create AppConfig from environment
   └── Initialize Container
       ├── Create config (Singleton)
       ├── Create llm_service (Singleton)
       │   └── Inject: model, host from config
       ├── Create vector_store (Singleton)
       │   └── Inject: connection_string, collection_name from config
       └── Register memory_use_case (Factory)
           └── Inject: llm_service, vector_store

2. Request Handling
   ├── HTTP Request arrives at router
   ├── FastAPI calls @inject decorated function
   ├── Container provides memory_use_case
   │   ├── Container creates new MemoryUseCase instance
   │   └── Injects llm_service and vector_store
   └── Use case executes business logic
       ├── Calls llm_service.generate_response()
       ├── Calls llm_service.embed()
       └── Calls vector_store.insert()

3. Application Shutdown
   └── Container.shutdown_resources()
       ├── Close database connections
       └── Cleanup resources
```

## Provider Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│                    Singleton Providers                    │
│  (Created once, shared across all requests)              │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Config    │  │  LLM Service │  │ Vector Store │   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
│        │                 │                  │            │
│        └─────────────────┴──────────────────┘            │
│                          │                               │
│                    Shared State                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                    Factory Providers                      │
│  (New instance created for each request)                 │
│                                                           │
│  Request 1          Request 2          Request 3         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │ UseCase #1  │   │ UseCase #2  │   │ UseCase #3  │   │
│  └─────────────┘   └─────────────┘   └─────────────┘   │
│        │                 │                  │            │
│        └─────────────────┴──────────────────┘            │
│                          │                               │
│                Uses Shared Singletons                    │
└──────────────────────────────────────────────────────────┘
```

## Testing Flow

```
┌──────────────────────────────────────────────────────────┐
│                    Production Flow                        │
│                                                           │
│  Router → MemoryUseCase → OllamaService → Ollama API    │
│                        → PgVectorStore → PostgreSQL      │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                      Test Flow                            │
│                                                           │
│  Test → MemoryUseCase → MockLlmService (in-memory)      │
│                       → MockVectorStore (in-memory)      │
│                                                           │
│  Same interface, different implementation!               │
└──────────────────────────────────────────────────────────┘
```

## Key Benefits

### 1. Dependency Inversion Principle
```
High-level modules (Use Cases) don't depend on low-level modules (Services)
Both depend on abstractions (Interfaces)

MemoryUseCase ──depends on──> LlmInterface <──implements── OllamaService
```

### 2. Open/Closed Principle
```
Easy to extend without modifying existing code:

LlmInterface
    ├── OllamaService (current)
    ├── OpenAIService (future)
    └── AnthropicService (future)

Just implement the interface and register in container!
```

### 3. Single Responsibility
```
Each component has one reason to change:

- Config: Environment changes
- Container: Dependency wiring changes
- Use Case: Business logic changes
- Service: External API changes
```

### 4. Testability
```
Easy to test in isolation:

Test MemoryUseCase:
    ├── Mock LlmInterface
    └── Mock BaseVectorStore

No need for real Ollama or PostgreSQL!
```

## Configuration Flow

```
.env file
    │
    ▼
Environment Variables
    │
    ▼
AppConfig.from_env()
    │
    ├── DatabaseConfig
    ├── LLMConfig
    └── VectorStoreConfig
    │
    ▼
Container Providers
    │
    ├── llm_service(model=config.llm.model)
    └── vector_store(connection_string=config.db.connection_string)
    │
    ▼
Service Instances
```

## Summary

The dependency injection setup provides:

1. **Loose Coupling**: Components depend on interfaces, not implementations
2. **Easy Testing**: Mock dependencies for unit tests
3. **Flexibility**: Swap implementations without changing code
4. **Configuration Management**: Centralized, type-safe configuration
5. **Lifecycle Management**: Automatic resource initialization and cleanup
6. **Clean Architecture**: Clear separation of concerns across layers
