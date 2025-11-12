#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 12, 2025 21:04:20$"

from abc import ABC, abstractmethod


class ExtractorInterface(ABC):
    @abstractmethod
    def extract(self, *args, **kwargs):
        pass


class OllamaExtractorService(ExtractorInterface):
    def extract(self, *args, **kwargs):
        pass
