#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 22, 2025 11:12:45$"

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
# This searches for .env in current directory and parent directories
load_dotenv()

# Alternative: Load from specific path
# env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
# load_dotenv(dotenv_path=env_path)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5440"))
    database: str = os.getenv("DB_NAME", "ai_mem")
    user: str = os.getenv("DB_USER", "ai_mem_user")
    password: str = os.getenv("DB_PASSWORD", "ai_mem_pass")
    min_connections: int = int(os.getenv("DB_MIN_CONN", "1"))
    max_connections: int = int(os.getenv("DB_MAX_CONN", "5"))

    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class LLMConfig:
    """LLM service configuration."""
    model: str = os.getenv("LLM_MODEL", "llama3.2:latest")
    host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    collection_name: str = os.getenv("VECTOR_COLLECTION", "temp_memory")


@dataclass
class AppConfig:
    """Application-wide configuration."""
    database: DatabaseConfig
    llm: LLMConfig
    vector_store: VectorStoreConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            database=DatabaseConfig(),
            llm=LLMConfig(),
            vector_store=VectorStoreConfig(),
        )
