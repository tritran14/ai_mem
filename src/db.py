#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 09, 2025 16:55:58$"

from sqlmodel import SQLModel, create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://ai_mem_user:ai_mem_pass@localhost:5440/ai_mem")

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)
