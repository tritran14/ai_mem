#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 08, 2025 16:22:03$"

from fastapi import FastAPI

from ai_mem.server.api.router import router as ai_mem_router

app = FastAPI(
    title="ai-mem API",
    description="API for managing and searching memories for your AI Agents and Apps.",
    version="1.0.0",
)
version = 1

app.include_router(
    router=ai_mem_router,
    prefix=f"/api/v{version}/ai-mem",
    tags=["ai-mem"]
)
