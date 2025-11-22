#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 12, 2025 21:03:45$"

import logging

from ai_mem.server.application.dto.memory import CreateMemoryRequest
from ai_mem.server.application.interface.llm import LlmInterface
from ai_mem.server.application.interface.vector_store import BaseVectorStore
from ai_mem.server.domain.const.prompt import FACT_RETRIEVAL_PROMPT
from ai_mem.server.infrastructure.empty_facts_logger import get_empty_facts_logger
from ai_mem.server.infrastructure.utils.llm_response_parser import parse_facts_from_response

logger = logging.getLogger(__name__)


class MemoryUseCase:
    def __init__(
        self,
        llm_service: LlmInterface,
        vector_store: BaseVectorStore,
    ):
        """
        Initialize MemoryUseCase with injected dependencies.
        
        Args:
            llm_service: LLM service for embeddings and text generation
            vector_store: Vector store for memory persistence
        """
        self.llm_service = llm_service
        self.vector_store = vector_store

    def add(self, request: CreateMemoryRequest):
        """
        Add new memories from user message.
        
        Extracts facts from the message, generates embeddings,
        and stores them in the vector database.
        
        Args:
            request: Memory creation request with user message
            
        Returns:
            dict: Summary of created memories
        """
        message = request.text
        user_id = request.user_id
        
        # Extract facts from message
        facts = self._get_facts(message)
        
        if not facts:
            logger.warning(f"No facts extracted from message: {message}")
            return {
                "success": False,
                "message": "No facts extracted",
                "facts_count": 0,
            }
        
        logger.info(f"Processing {len(facts)} facts for user {user_id}")
        
        # Store each fact as a memory
        created_memories = []
        failed_memories = []
        
        for i, fact in enumerate(facts, 1):
            try:
                logger.debug(f"Processing fact {i}/{len(facts)}: {fact}")
                
                # Generate embedding for the fact
                embedding = self.llm_service.embed(fact)
                
                # Prepare metadata
                metadata = {
                    "user_id": user_id,
                    "original_message": message,
                    "fact": fact,
                    **request.metadata,  # Include any additional metadata
                }
                
                # Create memory in vector store
                memory_id = self._create_memory(
                    data=fact,
                    embedding=embedding,
                    metadata=metadata,
                )
                
                created_memories.append({
                    "id": memory_id,
                    "fact": fact,
                })
                
                logger.debug(f"✓ Stored fact {i}/{len(facts)}: {memory_id}")
                
            except Exception as e:
                logger.error(f"Failed to store fact {i}/{len(facts)}: {fact}")
                logger.exception(f"Error: {e}")
                failed_memories.append({
                    "fact": fact,
                    "error": str(e),
                })
        
        # Log summary
        logger.info(
            f"Memory creation complete: "
            f"{len(created_memories)} succeeded, "
            f"{len(failed_memories)} failed"
        )
        
        return {
            "success": len(created_memories) > 0,
            "message": f"Created {len(created_memories)} memories",
            "facts_count": len(facts),
            "created_count": len(created_memories),
            "failed_count": len(failed_memories),
            "memories": created_memories,
            "failures": failed_memories if failed_memories else None,
        }

    def _create_memory(
        self,
        data: str,
        embedding: list,
        metadata: dict = None,
    ) -> str:
        """
        Create a memory in the vector store.
        
        Args:
            data: The fact/memory text
            embedding: Vector embedding of the fact
            metadata: Additional metadata (user_id, timestamp, etc.)
            
        Returns:
            str: Memory ID
        """
        import uuid
        from datetime import datetime
        
        # Generate unique memory ID
        memory_id = str(uuid.uuid4())
        
        # Add timestamp to metadata
        if metadata is None:
            metadata = {}
        
        metadata["created_at"] = datetime.utcnow().isoformat()
        metadata["data"] = data  # Store the actual fact text
        
        # Store in vector database
        self.vector_store.insert(
            vector=embedding[0] if isinstance(embedding, list) and len(embedding) > 0 else embedding,
            vector_id=memory_id,
            payload=metadata,
        )
        
        logger.debug(f"Created memory {memory_id}: {data[:50]}...")
        
        return memory_id

    def _get_facts(self, message: str) -> list[str]:
        """
        Extract facts from message using LLM.
        
        Args:
            message: Input message to extract facts from
            
        Returns:
            List of extracted facts, or empty list if none found
        """
        system_prompt, user_prompt = self._get_fact_retrieval_prompt(message)
        
        try:
            response = self.llm_service.generate_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            
            # Parse facts from response
            facts = parse_facts_from_response(response)
            
            if facts:
                logger.info(f"✓ Extracted {len(facts)} facts from message")
            else:
                # Log to dedicated empty facts file for analysis
                empty_facts_logger = get_empty_facts_logger()
                empty_facts_logger.log_empty_facts(message, response)
                logger.warning(f"No facts extracted - logged to empty_facts.log")
            
            return facts
            
        except Exception as e:
            logger.error(f"Error extracting facts: {e}")
            logger.exception("Full traceback:")
            return []

    @classmethod
    def _get_fact_retrieval_prompt(cls, input_message):
        return FACT_RETRIEVAL_PROMPT, f"Input:\n{input_message}"
