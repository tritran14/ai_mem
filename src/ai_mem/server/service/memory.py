#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 12, 2025 21:03:45$"

from abc import ABC, abstractmethod


class MemoryInterface(ABC):
    @abstractmethod
    def add(self, messages, *args, **kwargs):
        pass


class MemoryService(MemoryInterface):
    def __init__(self):
        self.extractor = None
        self.vector_store = None

    def add(self, messages, *args, **kwargs):
        pass

    def _add_to_vector_store(self, messages, *args, **kwargs):
        pass

    def _extract_fact(self, messages, *args, **kwargs):
        pass

    def _search_vector_store(self, query, *args, **kwargs):
        pass
