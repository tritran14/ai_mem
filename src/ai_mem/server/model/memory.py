#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 09, 2025 11:43:11$"

from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Relationship, Column, String
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

from src.ai_mem.server.model.user import User

EMBED_DIM = 1536


class Memory(SQLModel, table=True):
    __tablename__ = "memories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    agent_id: UUID | None = Field(default=None)
    type: str = Field(default="observation", sa_column=Column(String(32)))
    content: str = Field(sa_column=Column(String))
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(EMBED_DIM), nullable=True)
    )
    importance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship(back_populates="memories")
    sessions: list["MemorySession"] = Relationship(back_populates="memory")
    sources: list["MemorySource"] = Relationship(back_populates="memory")


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    agent_id: UUID | None = Field(default=None)
    topic: str | None = Field(default=None, sa_column=Column(String))
    meta: dict | None = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship(back_populates="sessions")
    memories: list["MemorySession"] = Relationship(back_populates="session")


class MemorySession(SQLModel, table=True):
    __tablename__ = "memory_sessions"

    memory_id: UUID = Field(foreign_key="memories.id", primary_key=True)
    session_id: UUID = Field(foreign_key="sessions.id", primary_key=True)

    memory: Memory | None = Relationship(back_populates="sessions")
    session: Session | None = Relationship(back_populates="memories")


class MemorySource(SQLModel, table=True):
    __tablename__ = "memory_sources"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    memory_id: UUID = Field(foreign_key="memories.id")
    source_type: str | None = Field(default=None, sa_column=Column(String(64)))
    source_ref: str | None = Field(default=None, sa_column=Column(String))
    meta: dict | None = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    memory: Memory | None = Relationship(back_populates="sources")
