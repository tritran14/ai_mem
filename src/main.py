#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 08, 2025 16:22:03$"

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from ai_mem.server.infrastructure.container import Container
from ai_mem.server.infrastructure.logging_config import setup_logging
from ai_mem.server.interface_adapter.rest.router import router as ai_mem_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan - initialize and cleanup resources.
    """
    # Setup logging first
    setup_logging()
    logger.info("Starting ai-mem application...")
    
    # Startup: Initialize DI container
    container = Container()
    container.wire(modules=["ai_mem.server.interface_adapter.rest.router"])
    app.state.container = container
    logger.info("Dependency injection container initialized")
    
    yield
    
    # Shutdown: Close container resources
    logger.info("Shutting down ai-mem application...")
    await container.shutdown_resources()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="ai-mem API",
    description="API for managing and searching memories for your AI Agents and Apps.",
    version="1.0.0",
    lifespan=lifespan,
)

version = 1

app.include_router(
    router=ai_mem_router,
    prefix=f"/api/v{version}/ai-mem",
    tags=["ai-mem"]
)

