#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 12, 2025 21:08:01$"

import logging

from ai_mem.server.llm_client.base import BaseLlmClient
from ollama import Client

logger = logging.getLogger(__name__)


class OllamaClient(BaseLlmClient):
    def __init__(self):
        super().__init__()
        self.model = "llama2"
        self.client = Client()

        local_models = self.client.list()["models"]
        if not any(model.get("name") == self.model for model in local_models):
            logger.info(f"Pulling {self.model} from Ollama!")
            self.client.pull(self.model)
