# Dependency Injection Quick Reference

## Common Patterns & Code Snippets

### 1. Adding a New Service

#### Step 1: Define Interface (Domain Layer)
```python
# src/ai_mem/server/application/interface/my_service.py
from abc import ABC, abstractmethod

class MyServiceInterface(ABC):
    @abstractmethod
    def do_something(self, param: str) -> str:
        """Do something with the parameter."""
        pass
```

#### Step 2: Implement Service (Infrastructure Layer)
```python
# src/ai_mem/server/infrastructure/service/my_service.py
from ai_mem.server.application.interface.my_service import MyServiceInterface

class MyServiceImpl(MyServiceInterface):
    def __init__(self, config_value: str):
        self.config_value = config_value
    
    def do_something(self, param: str) -> str:
        return f"{self.config_value}: {param}"
```

#### Step 3: Add Configuration (if needed)
```python
# src/ai_mem/server/infrastructure/config.py
@dataclass
class MyServiceConfig:
    value: str = os.getenv("MY_SERVICE_VALUE", "default")

# Add to AppConfig
@dataclass
class AppConfig:
    # ... existing configs ...
    my_service: MyServiceConfig
```

#### Step 4: Register in Container
```python
# src/ai_mem/server/infrastructure/container.py
class Container(containers.DeclarativeContainer):
    # ... existing providers ...
    
    my_service = providers.Singleton(
        MyServiceImpl,
        config_value=config.provided.my_service.value,
    )
```

#### Step 5: Inject into Use Case
```python
# src/ai_mem/server/application/use_case/my_use_case.py
class MyUseCase:
    def __init__(
        self,
        my_service: MyServiceInterface,
    ):
        self.my_service = my_service
    
    def execute(self, param: str):
        return self.my_service.do_something(param)
```

#### Step 6: Register Use Case in Container
```python
# src/ai_mem/server/infrastructure/container.py
my_use_case = providers.Factory(
    MyUseCase,
    my_service=my_service,
)
```

#### Step 7: Use in Router
```python
# src/ai_mem/server/interface_adapter/rest/router.py
from dependency_injector.wiring import Provide, inject
from fastapi import Depends

@router.post("/my-endpoint")
@inject
def my_endpoint(
    param: str,
    use_case: MyUseCase = Depends(Provide[Container.my_use_case]),
):
    result = use_case.execute(param)
    return {"result": result}
```

---

### 2. Provider Types

#### Singleton (One instance shared)
```python
# Use for: Services with state, expensive to create
service = providers.Singleton(
    MyService,
    param1=value1,
    param2=value2,
)
```

#### Factory (New instance each time)
```python
# Use for: Stateless use cases, request-scoped objects
use_case = providers.Factory(
    MyUseCase,
    service=service,
)
```

#### Configuration (Static values)
```python
# Use for: Configuration values
api_key = providers.Configuration()
api_key.from_dict({"key": "value"})
```

---

### 3. Testing Patterns

#### Unit Test with Mocks
```python
from unittest.mock import Mock

def test_use_case():
    # Create mock
    mock_service = Mock(spec=MyServiceInterface)
    mock_service.do_something.return_value = "mocked result"
    
    # Inject mock
    use_case = MyUseCase(my_service=mock_service)
    
    # Test
    result = use_case.execute("test")
    
    # Assert
    assert result == "mocked result"
    mock_service.do_something.assert_called_once_with("test")
```

#### Integration Test with Container
```python
def test_with_container():
    from ai_mem.server.infrastructure.container import Container
    
    # Create container
    container = Container()
    
    # Get use case
    use_case = container.my_use_case()
    
    # Test with real dependencies
    result = use_case.execute("test")
    assert result is not None
```

#### Custom Mock Implementation
```python
class MockMyService(MyServiceInterface):
    def __init__(self):
        self.calls = []
    
    def do_something(self, param: str) -> str:
        self.calls.append(param)
        return f"mock: {param}"

def test_with_custom_mock():
    mock = MockMyService()
    use_case = MyUseCase(my_service=mock)
    
    use_case.execute("test")
    
    assert "test" in mock.calls
```

---

### 4. Configuration Patterns

#### Environment Variable
```python
# .env
MY_CONFIG_VALUE=production_value

# config.py
@dataclass
class MyConfig:
    value: str = os.getenv("MY_CONFIG_VALUE", "default")
```

#### Nested Configuration
```python
@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.host}:{self.port}"

@dataclass
class AppConfig:
    database: DatabaseConfig
```

#### Configuration Injection
```python
# Container
service = providers.Singleton(
    MyService,
    host=config.provided.database.host,
    port=config.provided.database.port,
)
```

---

### 5. Router Patterns

#### Simple Injection
```python
@router.get("/endpoint")
@inject
def endpoint(
    use_case: MyUseCase = Depends(Provide[Container.my_use_case]),
):
    return use_case.execute()
```

#### Multiple Dependencies
```python
@router.post("/endpoint")
@inject
def endpoint(
    request: MyRequest,
    use_case1: UseCase1 = Depends(Provide[Container.use_case1]),
    use_case2: UseCase2 = Depends(Provide[Container.use_case2]),
):
    result1 = use_case1.execute(request)
    result2 = use_case2.execute(result1)
    return {"result": result2}
```

#### With Path Parameters
```python
@router.get("/items/{item_id}")
@inject
def get_item(
    item_id: str,
    use_case: MyUseCase = Depends(Provide[Container.my_use_case]),
):
    return use_case.get_by_id(item_id)
```

---

### 6. Common Mistakes & Solutions

#### ❌ Mistake: Forgetting @inject
```python
# Wrong - dependency won't be injected
def endpoint(
    use_case: MyUseCase = Depends(Provide[Container.my_use_case]),
):
    pass
```

#### ✅ Solution: Add @inject
```python
# Correct
@inject
def endpoint(
    use_case: MyUseCase = Depends(Provide[Container.my_use_case]),
):
    pass
```

---

#### ❌ Mistake: Module not wired
```python
# Wrong - module not in wiring list
container.wire(modules=["ai_mem.server.interface_adapter.rest.router"])
# But using DI in ai_mem.server.interface_adapter.rest.other_router
```

#### ✅ Solution: Add module to wiring
```python
# Correct
container.wire(modules=[
    "ai_mem.server.interface_adapter.rest.router",
    "ai_mem.server.interface_adapter.rest.other_router",
])
```

---

#### ❌ Mistake: Depending on implementation
```python
# Wrong - depends on concrete class
class MyUseCase:
    def __init__(self, service: OllamaService):
        self.service = service
```

#### ✅ Solution: Depend on interface
```python
# Correct - depends on interface
class MyUseCase:
    def __init__(self, service: LlmInterface):
        self.service = service
```

---

#### ❌ Mistake: Creating dependencies inside
```python
# Wrong - creates dependency inside
class MyUseCase:
    def __init__(self):
        self.service = OllamaService()
```

#### ✅ Solution: Inject dependencies
```python
# Correct - injects dependency
class MyUseCase:
    def __init__(self, service: LlmInterface):
        self.service = service
```

---

### 7. Debugging Tips

#### Check if container is wired
```python
# In main.py or startup
container = Container()
container.wire(modules=["your.module"])
print(f"Wired: {container.wiring_config.modules}")
```

#### Verify provider exists
```python
# Check if provider is registered
container = Container()
print(hasattr(container, 'my_service'))  # Should be True
```

#### Test dependency resolution
```python
# Manually resolve dependency
container = Container()
service = container.my_service()
print(f"Service: {service}")
```

#### Check configuration
```python
# Verify configuration is loaded
config = AppConfig.from_env()
print(f"Config: {config}")
```

---

### 8. Quick Commands

```bash
# Install dependencies
poetry install --with dev

# Run application
poetry run uvicorn src.main:app --reload

# Run tests
poetry run pytest tests/ -v

# Run specific test
poetry run pytest tests/test_file.py::test_function -v

# Check types
poetry run mypy src/

# Format code
poetry run black src/

# Lint code
poetry run ruff src/
```

---

### 9. File Templates

#### New Interface
```python
#! /usr/bin/python
from abc import ABC, abstractmethod

class MyServiceInterface(ABC):
    @abstractmethod
    def method_name(self, param: str) -> str:
        """Method description."""
        pass
```

#### New Service Implementation
```python
#! /usr/bin/python
from ai_mem.server.application.interface.my_service import MyServiceInterface

class MyServiceImpl(MyServiceInterface):
    def __init__(self, config_param: str):
        self.config_param = config_param
    
    def method_name(self, param: str) -> str:
        # Implementation
        return f"{self.config_param}: {param}"
```

#### New Use Case
```python
#! /usr/bin/python
from ai_mem.server.application.interface.my_service import MyServiceInterface

class MyUseCase:
    def __init__(self, my_service: MyServiceInterface):
        """
        Initialize use case with dependencies.
        
        Args:
            my_service: Service for doing something
        """
        self.my_service = my_service
    
    def execute(self, param: str) -> dict:
        """
        Execute the use case.
        
        Args:
            param: Input parameter
            
        Returns:
            Result dictionary
        """
        result = self.my_service.method_name(param)
        return {"result": result}
```

---

### 10. Environment Variables Template

```bash
# .env

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=user
DB_PASSWORD=pass

# LLM Service
LLM_MODEL=llama3.2:latest
OLLAMA_HOST=http://localhost:11434

# Vector Store
VECTOR_COLLECTION=memories

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

---

## Quick Reference Card

| Task | Pattern |
|------|---------|
| Define interface | `class XInterface(ABC)` |
| Implement service | `class XImpl(XInterface)` |
| Register singleton | `providers.Singleton(X, ...)` |
| Register factory | `providers.Factory(X, ...)` |
| Inject in route | `@inject` + `Depends(Provide[...])` |
| Inject in use case | Constructor parameter |
| Add config | Add to `config.py` + `AppConfig` |
| Test with mock | `Mock(spec=XInterface)` |
| Wire module | `container.wire(modules=[...])` |

---

## Need Help?

1. Check [DEPENDENCY_INJECTION.md](./DEPENDENCY_INJECTION.md) for detailed guide
2. See [QUICK_START.md](./QUICK_START.md) for setup instructions
3. Review [test examples](../tests/test_dependency_injection_example.py)
4. Consult [dependency-injector docs](https://python-dependency-injector.ets-labs.org/)
