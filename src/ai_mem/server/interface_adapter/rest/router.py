#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 16, 2025 15:23:05$"

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from ai_mem.server.application.dto.memory import CreateMemoryRequest
from ai_mem.server.application.use_case.memory import MemoryUseCase
from ai_mem.server.infrastructure.container import Container

router = APIRouter()


@router.get("/home")
def home():
    return {"message": "Welcome to the ai-mem API!"}


@router.post("/")
@inject
def create_memory(
    request: CreateMemoryRequest,
    memory_use_case: MemoryUseCase = Depends(Provide[Container.memory_use_case]),
):
    """
    Create new memory entries from user message.
    
    Extracts facts from the message and stores them as memories
    in the vector database.
    
    Args:
        request: Memory creation request with user message
        memory_use_case: Injected MemoryUseCase dependency
    
    Returns:
        dict: Summary of created memories including:
            - success: Whether any memories were created
            - message: Summary message
            - facts_count: Number of facts extracted
            - created_count: Number of memories created
            - failed_count: Number of failures
            - memories: List of created memory IDs and facts
            - failures: List of failed facts (if any)
    """
    result = memory_use_case.add(request)
    return result

