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

app = FastAPI(
    title="ai-mem API",
    description="API for managing and searching memories for your AI Agents and Apps.",
    version="1.0.0",
)
