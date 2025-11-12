#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 11, 2025 22:47:35$"


from pydantic import BaseModel

class CreateMemoryRequest(BaseModel):
    user_id: str
    text: str
    metadata: dict = {}
    infer: bool = True
    app: str = "openmemory"
