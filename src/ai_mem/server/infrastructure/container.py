#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 22, 2025 11:12:45$"

from dependency_injector import containers, providers

from ai_mem.server.application.use_case.memory import MemoryUseCase
from ai_mem.server.infrastructure.config import AppConfig
from ai_mem.server.infrastructure.service.llm.ollama import OllamaService
from ai_mem.server.infrastructure.service.vector_store.pgvector import PgVectorStore


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container following Clean Architecture principles.
    
    This container manages all dependencies and their lifecycles:
    - Configuration: Application settings
    - Infrastructure: External services (LLM, Vector Store, Database)
    - Use Cases: Business logic
    """

    # Configuration
    config = providers.Singleton(AppConfig.from_env)

    # Infrastructure Layer - External Services
    llm_service = providers.Singleton(
        OllamaService,
        model=config.provided.llm.model,
        host=config.provided.llm.host,
    )

    vector_store = providers.Singleton(
        PgVectorStore,
        dbname=config.provided.database.database,
        collection_name=config.provided.vector_store.collection_name,
        minconn=config.provided.database.min_connections,
        maxconn=config.provided.database.max_connections,
        connection_string=config.provided.database.connection_string,
    )

    # Application Layer - Use Cases
    memory_use_case = providers.Factory(
        MemoryUseCase,
        llm_service=llm_service,
        vector_store=vector_store,
    )

    # Wiring configuration - automatically inject dependencies in these modules
    # Best Practice: Only wire modules that actually use @inject decorator
    # This improves performance and makes dependency injection explicit
    wiring_config = containers.WiringConfiguration(
        modules=[
            # Interface Adapters - Entry points that need DI
            "ai_mem.server.interface_adapter.rest.router",
            # Add more modules here as needed:
            # "ai_mem.server.interface_adapter.rest.another_router",
            # "ai_mem.server.interface_adapter.cli.commands",
        ]
    )
