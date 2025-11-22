# AI Memory Layer

A memory layer for LLM applications, inspired by [mem0](https://github.com/mem0ai/mem0), built with Clean Architecture principles and dependency injection.

## 🎯 Overview

AI Memory provides a persistent memory layer for AI agents and applications, allowing them to remember and recall information across conversations. The project is built following Clean Architecture principles with proper dependency injection using `dependency-injector`.

## ✨ Features

- **Memory Management**: Store and retrieve memories for AI agents
- **Vector Search**: Efficient similarity search using pgvector
- **LLM Integration**: Extract facts and generate embeddings using Ollama
- **Clean Architecture**: Proper separation of concerns across layers
- **Dependency Injection**: Fully configured DI container for easy testing and flexibility
- **Type-Safe Configuration**: Environment-based configuration with type safety

## 🏗️ Architecture

This project follows Clean Architecture with clear separation between:

- **Domain Layer**: Business rules and interfaces
- **Application Layer**: Use cases and business logic
- **Infrastructure Layer**: External services (LLM, Vector Store, Database)
- **Interface Adapters**: REST API endpoints

### Dependency Injection

The project uses `dependency-injector` to manage dependencies:

```python
# Dependencies are automatically injected
@router.post("/")
@inject
def create_memory(
    request: CreateMemoryRequest,
    memory_use_case: MemoryUseCase = Depends(Provide[Container.memory_use_case]),
):
    memory_use_case.add(request)
    return {"success": True}
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running quickly
- **[Dependency Injection Guide](docs/DEPENDENCY_INJECTION.md)** - Detailed DI architecture
- **[Architecture Diagram](docs/ARCHITECTURE_DIAGRAM.md)** - Visual architecture overview
- **[Empty Facts Logger](docs/EMPTY_FACTS_LOGGER.md)** - Debugging empty facts
- **[Logging Guide](docs/LOGGING_GUIDE.md)** - Complete logging documentation

## 📋 Project Planning

- **[BACKLOG.md](BACKLOG.md)** - Detailed project backlog with 3 development phases
- **[TODO.md](TODO.md)** - Quick TODO list with current priorities

### Development Phases:
1. **Phase 1: Ingestion Pipeline** 🟡 In Progress (30%)
2. **Phase 2: Semantic Retrieval** 🔴 Not Started
3. **Phase 3: Logic Engine** 🔴 Not Started

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- PostgreSQL with pgvector extension
- Ollama running locally

### Installation

```bash
# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start the server
poetry run uvicorn src.main:app --reload
```

Visit `http://localhost:8000/docs` for API documentation.

## 🧪 Testing

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest tests/ -v
```

## 📁 Project Structure

```
src/ai_mem/server/
├── application/          # Application Layer
│   ├── dto/             # Data Transfer Objects
│   ├── interface/       # Abstract interfaces
│   └── use_case/        # Business logic
├── domain/              # Domain Layer
│   └── const/          # Constants and prompts
├── infrastructure/      # Infrastructure Layer
│   ├── config.py       # Configuration
│   ├── container.py    # DI Container
│   └── service/        # Service implementations
└── interface_adapter/   # Interface Adapters
    └── rest/           # REST API
```

## 🔧 Configuration

All configuration is managed through environment variables. See `.env.example` for available options:

- Database connection settings
- LLM model configuration
- Vector store settings

## 🤝 Contributing

This is a personal project inspired by mem0. Feel free to explore and learn from the clean architecture implementation.

## 📝 License

Copyright (C) 2025 Paradox

## 🙏 Acknowledgments

- Inspired by [mem0](https://github.com/mem0ai/mem0)
- Built with Clean Architecture principles
- Uses `dependency-injector` for DI