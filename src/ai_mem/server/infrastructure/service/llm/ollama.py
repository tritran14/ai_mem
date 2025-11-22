#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 16, 2025 15:31:15$"

import logging

from ollama import Client

from ai_mem.server.application.interface.llm import LlmInterface

logger = logging.getLogger(__name__)


class OllamaService(LlmInterface):
    def __init__(self, model: str = "llama3.2:latest", host: str = "http://localhost:11434"):
        super().__init__()
        self.model = model
        self._client = Client(host=host)

        local_models = self._client.list()["models"]
        if not any(model.get("model") == self.model for model in local_models):
            logger.info(f"Pulling {self.model} from Ollama!")
            self._client.pull(self.model)

    def embed(self, input_message: str):
        return self._client.embed(
            model=self.model,
            input=input_message,
        ).get("embeddings")

    def generate_response(
        self,
        messages: list[dict[str, str]],
    ):
        params = dict(
            model=self.model,
            messages=messages,
        )

        res = self._client.chat(**params)
        return self._parse_response(res)

    @classmethod
    def _parse_response(cls, response):
        if isinstance(response, dict):
            content = response["message"]["content"]
        else:
            content = response.message.content

        return content
