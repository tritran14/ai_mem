#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 17, 2025 15:23:40$"

from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

EMBED_DIM = 3072


class TempMemory(SQLModel, table=True):
    __tablename__ = "temp_memory"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    vector: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(EMBED_DIM), nullable=True)
    )
    payload: dict | None = Field(default=None, sa_column=Column(JSONB))
