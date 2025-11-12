#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 09, 2025 16:11:37$"

from datetime import datetime

from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Relationship, Column, String
from sqlalchemy.dialects.postgresql import JSONB


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str | None = Field(default=None, sa_column=Column(String(255)))
    meta: dict | None = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sessions: list["Session"] = Relationship(back_populates="user")
    memories: list["Memory"] = Relationship(back_populates="user")
