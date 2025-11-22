# Dependency Injection Architecture

This document explains how dependency injection is implemented in the ai-mem project following Clean Architecture principles.

## Overview

The project uses the `dependency-injector` library to manage dependencies across different layers:

```
┌─────────────────────────────────────────┐
│     Interface Adapters (REST API)      │
│         (router.py)                     │
└──────────────┬──────────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────────┐
│      Application Layer (Use Cases)      │
│         (MemoryUseCase)                 │
└──────────────┬──────────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────────┐
│    Domain Layer (Interfaces/Protocols)  │
│  (LlmInterface, BaseVectorStore)        │
└──────────────┬──────────────────────────┘
               │ implemented by
               ▼
┌─────────────────────────────────────────┐
│   Infrastructure Layer (Services)       │
│  (OllamaService, PgVectorStore)         │
└─────────────────────────────────────────┘
```

## Key Components

### 1. Configuration (`infrastructure/config.py`)

Centralized configuration management using dataclasses and environment variables:

```python
from ai_mem.server.infrastructure.config import AppConfig

config = AppConfig.from_env()
```

**Benefits:**
- Type-safe configuration
- Environment variable support
- Easy testing with different configs
- Single source of truth

### 2. Container (`infrastructure/container.py`)

The DI container manages all dependencies and their lifecycles:

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Singleton(AppConfig.from_env)
    
    # Services
    llm_service = providers.Singleton(OllamaService, ...)
    vector_store = providers.Singleton(PgVectorStore, ...)
    
    # Use Cases
    memory_use_case = providers.Factory(MemoryUseCase, ...)
```

**Provider Types:**
- `Singleton`: Single instance shared across the application (services)
- `Factory`: New instance created for each request (use cases)

### 3. Dependency Injection in Routes

Routes use the `@inject` decorator and `Depends` to receive dependencies:

```python
from dependency_injector.wiring import Provide, inject
from fastapi import Depends

@router.post("/")
@inject
def create_memory(
    request: CreateMemoryRequest,
    memory_use_case: MemoryUseCase = Depends(Provide[Container.memory_use_case]),
):
    memory_use_case.add(request)
    return {"success": True}
```

### 4. Application Initialization (`main.py`)

The container is initialized during FastAPI startup:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    container = Container()
    container.wire(modules=["ai_mem.server.interface_adapter.rest.router"])
    app.state.container = container
    
    yield
    
    # Shutdown
    await container.shutdown_resources()
```

## Clean Architecture Benefits

### 1. **Dependency Inversion Principle**
- High-level modules (use cases) don't depend on low-level modules (services)
- Both depend on abstractions (interfaces)
- Example: `MemoryUseCase` depends on `LlmInterface`, not `OllamaService`

### 2. **Single Responsibility**
- Each layer has a clear responsibility
- Configuration is separate from business logic
- Infrastructure is isolated from application logic

### 3. **Open/Closed Principle**
- Easy to add new implementations without modifying existing code
- Example: Add a new LLM service by implementing `LlmInterface`

### 4. **Testability**
- Easy to mock dependencies in tests
- Can inject test doubles without changing production code

```python
# Testing example
def test_memory_use_case():
    mock_llm = MockLlmService()
    mock_vector = MockVectorStore()
    use_case = MemoryUseCase(llm_service=mock_llm, vector_store=mock_vector)
    # Test use case with mocks
```

## Adding New Dependencies

### Step 1: Define Interface (Domain Layer)

```python
# server/application/interface/new_service.py
from abc import ABC, abstractmethod

class NewServiceInterface(ABC):
    @abstractmethod
    def do_something(self):
        pass
```

### Step 2: Implement Service (Infrastructure Layer)

```python
# server/infrastructure/service/new_service.py
from ai_mem.server.application.interface.new_service import NewServiceInterface

class NewServiceImpl(NewServiceInterface):
    def __init__(self, config_param: str):
        self.config_param = config_param
    
    def do_something(self):
        # Implementation
        pass
```

### Step 3: Register in Container

```python
# server/infrastructure/container.py
class Container(containers.DeclarativeContainer):
    # ... existing providers ...
    
    new_service = providers.Singleton(
        NewServiceImpl,
        config_param=config.provided.some_config,
    )
```

### Step 4: Inject into Use Case

```python
# server/application/use_case/some_use_case.py
class SomeUseCase:
    def __init__(
        self,
        new_service: NewServiceInterface,
    ):
        self.new_service = new_service
```

### Step 5: Update Container Factory

```python
# server/infrastructure/container.py
some_use_case = providers.Factory(
    SomeUseCase,
    new_service=new_service,
)
```

## Configuration Management

All configuration is managed through environment variables:

1. Copy `.env.example` to `.env`
2. Update values as needed
3. Configuration is automatically loaded on startup

```bash
cp .env.example .env
# Edit .env with your values
```

## Best Practices

### 1. **Always Use Interfaces**
```python
# ✅ Good - depends on interface
def __init__(self, llm: LlmInterface):
    self.llm = llm

# ❌ Bad - depends on concrete implementation
def __init__(self, llm: OllamaService):
    self.llm = llm
```

### 2. **Constructor Injection**
```python
# ✅ Good - dependencies injected via constructor
class UseCase:
    def __init__(self, service: ServiceInterface):
        self.service = service

# ❌ Bad - creating dependencies inside
class UseCase:
    def __init__(self):
        self.service = ConcreteService()
```

### 3. **Configuration Over Hardcoding**
```python
# ✅ Good - configurable
def __init__(self, model: str):
    self.model = model

# ❌ Bad - hardcoded
def __init__(self):
    self.model = "llama3.2:latest"
```

### 4. **Proper Provider Types**
- Use `Singleton` for stateful services (DB connections, API clients)
- Use `Factory` for stateless use cases
- Use `Configuration` for config values

## Troubleshooting

### Issue: "Provider not found"
**Solution:** Make sure the module is wired in `container.wire()`

### Issue: "Circular dependency"
**Solution:** Review your dependency graph, consider using `Factory` instead of `Singleton`

### Issue: "Cannot inject dependency"
**Solution:** Ensure `@inject` decorator is applied to the function

## References

- [dependency-injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
