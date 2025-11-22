# Quick Start Guide - Dependency Injection Setup

This guide will help you get started with the dependency injection setup in ai-mem.

## Prerequisites

- Python 3.11+
- Poetry installed
- PostgreSQL with pgvector extension
- Ollama running locally (for LLM service)

## Installation

1. **Install dependencies:**
```bash
poetry install
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run database migrations:**
```bash
alembic upgrade head
```

## Running the Application

Start the FastAPI server:

```bash
poetry run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## Testing the Setup

### 1. Check API Documentation
Visit `http://localhost:8000/docs` to see the interactive API documentation.

### 2. Test the Memory Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/ai-mem/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love programming in Python",
    "user_id": "test-user-123"
  }'
```

### 3. Run Tests

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest tests/ -v
```

## Project Structure

```
ai_mem/
├── server/
│   ├── application/           # Application Layer (Use Cases)
│   │   ├── dto/              # Data Transfer Objects
│   │   ├── interface/        # Abstract interfaces (ports)
│   │   └── use_case/         # Business logic
│   │
│   ├── domain/               # Domain Layer (Business Rules)
│   │   └── const/           # Constants and prompts
│   │
│   ├── infrastructure/       # Infrastructure Layer
│   │   ├── config.py        # Configuration management
│   │   ├── container.py     # DI Container
│   │   └── service/         # Service implementations
│   │       ├── llm/         # LLM service (Ollama)
│   │       └── vector_store/ # Vector store (PgVector)
│   │
│   └── interface_adapter/    # Interface Adapters
│       └── rest/            # REST API (FastAPI)
│           └── router.py    # API routes
│
└── main.py                  # Application entry point
```

## How It Works

### 1. Configuration Loading
On startup, the application loads configuration from environment variables:

```python
# infrastructure/config.py
config = AppConfig.from_env()
```

### 2. Container Initialization
The DI container is created and wired during FastAPI startup:

```python
# main.py
container = Container()
container.wire(modules=["ai_mem.server.interface_adapter.rest.router"])
```

### 3. Dependency Injection
Dependencies are automatically injected into route handlers:

```python
# interface_adapter/rest/router.py
@router.post("/")
@inject
def create_memory(
    request: CreateMemoryRequest,
    memory_use_case: MemoryUseCase = Depends(Provide[Container.memory_use_case]),
):
    memory_use_case.add(request)
    return {"success": True}
```

### 4. Use Case Execution
The use case receives all its dependencies through constructor injection:

```python
# application/use_case/memory.py
class MemoryUseCase:
    def __init__(
        self,
        llm_service: LlmInterface,
        vector_store: BaseVectorStore,
    ):
        self.llm_service = llm_service
        self.vector_store = vector_store
```

## Configuration Options

All configuration is managed through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5440` |
| `DB_NAME` | Database name | `ai_mem` |
| `DB_USER` | Database user | `ai_mem_user` |
| `DB_PASSWORD` | Database password | `ai_mem_pass` |
| `LLM_MODEL` | Ollama model to use | `llama3.2:latest` |
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `VECTOR_COLLECTION` | Vector store collection name | `temp_memory` |

## Adding New Features

### Example: Adding a New Service

1. **Define the interface** (application/interface/):
```python
class NewServiceInterface(ABC):
    @abstractmethod
    def do_something(self):
        pass
```

2. **Implement the service** (infrastructure/service/):
```python
class NewServiceImpl(NewServiceInterface):
    def __init__(self, config_param: str):
        self.config_param = config_param
    
    def do_something(self):
        # Implementation
        pass
```

3. **Register in container** (infrastructure/container.py):
```python
new_service = providers.Singleton(
    NewServiceImpl,
    config_param=config.provided.some_config,
)
```

4. **Inject into use case**:
```python
class SomeUseCase:
    def __init__(self, new_service: NewServiceInterface):
        self.new_service = new_service
```

## Troubleshooting

### Issue: Import errors
**Solution:** Make sure you're running commands with `poetry run` or activate the virtual environment:
```bash
poetry shell
```

### Issue: Database connection errors
**Solution:** Verify PostgreSQL is running and credentials in `.env` are correct:
```bash
docker-compose up -d  # If using Docker
```

### Issue: Ollama not found
**Solution:** Make sure Ollama is installed and running:
```bash
ollama serve
```

### Issue: Dependencies not injected
**Solution:** Ensure the module is listed in `container.wire()` in `main.py`

## Next Steps

- Read [DEPENDENCY_INJECTION.md](./DEPENDENCY_INJECTION.md) for detailed architecture documentation
- Check [test_dependency_injection_example.py](../tests/test_dependency_injection_example.py) for testing examples
- Explore the [mem0 repository](https://github.com/mem0ai/mem0) for additional features

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [dependency-injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
