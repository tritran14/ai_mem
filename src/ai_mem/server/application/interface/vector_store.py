#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 17, 2025 13:39:27$"

from abc import ABC, abstractmethod


class BaseVectorStore(ABC):
    @abstractmethod
    def insert(self, vector, vector_id=None, payload=None):
        pass
