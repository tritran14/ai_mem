#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 11, 2025 22:28:19$"

from fastapi import APIRouter

from ai_mem.server.dto.memory import CreateMemoryRequest

router = APIRouter()


@router.get("/home")
def home():
    return {"message": "Welcome to the ai-mem API!"}


@router.post("/")
def create_memory(
    request: CreateMemoryRequest,
):

    return {"success": True}
