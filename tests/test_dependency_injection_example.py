#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 22, 2025 11:12:45$"

"""
Example tests demonstrating how to test with dependency injection.
This shows how clean architecture makes testing easier.
"""

import pytest
from unittest.mock import Mock

from ai_mem.server.application.dto.memory import CreateMemoryRequest
from ai_mem.server.application.interface.llm import LlmInterface
from ai_mem.server.application.interface.vector_store import BaseVectorStore
from ai_mem.server.application.use_case.memory import MemoryUseCase


class MockLlmService(LlmInterface):
    """Mock LLM service for testing."""
    
    def __init__(self):
        super().__init__()
        self.embed_calls = []
        self.generate_calls = []
    
    def embed(self, input_message: str):
        """Mock embed method that tracks calls."""
        self.embed_calls.append(input_message)
        # Return a fake embedding
        return [[0.1, 0.2, 0.3]]
    
    def generate_response(self, messages: list[dict[str, str]]):
        """Mock generate_response that returns fake facts."""
        self.generate_calls.append(messages)
        # Return a fake response with facts
        return '{"facts": ["User likes Python", "User is learning AI"]}'


class MockVectorStore(BaseVectorStore):
    """Mock vector store for testing."""
    
    def __init__(self):
        self.inserted_items = []
    
    def insert(self, vector, vector_id=None, payload=None):
        """Mock insert method that tracks calls."""
        self.inserted_items.append({
            'vector': vector,
            'vector_id': vector_id,
            'payload': payload
        })


class TestMemoryUseCase:
    """Test suite for MemoryUseCase demonstrating dependency injection."""
    
    def test_add_memory_with_mocks(self):
        """
        Test that MemoryUseCase.add() correctly uses injected dependencies.
        This demonstrates how DI makes testing easy - we can inject mocks!
        """
        # Arrange: Create mock dependencies
        mock_llm = MockLlmService()
        mock_vector_store = MockVectorStore()
        
        # Inject mocks into use case
        use_case = MemoryUseCase(
            llm_service=mock_llm,
            vector_store=mock_vector_store
        )
        
        # Create test request
        request = CreateMemoryRequest(
            text="I love programming in Python",
            user_id="test-user-123"
        )
        
        # Act: Call the method under test
        use_case.add(request)
        
        # Assert: Verify the use case called our mocks correctly
        assert len(mock_llm.generate_calls) == 1, "Should call LLM to extract facts"
        assert len(mock_llm.embed_calls) >= 1, "Should call LLM to create embeddings"
        
        # Verify the LLM was called with the right message
        generate_call = mock_llm.generate_calls[0]
        assert any("I love programming in Python" in msg.get("content", "") 
                  for msg in generate_call), "Should pass user message to LLM"
    
    def test_dependency_injection_flexibility(self):
        """
        Test that we can easily swap implementations.
        This demonstrates the Open/Closed Principle.
        """
        # We can use different mock implementations
        llm_v1 = MockLlmService()
        llm_v2 = MockLlmService()
        vector_store = MockVectorStore()
        
        # Create use cases with different LLM implementations
        use_case_v1 = MemoryUseCase(llm_service=llm_v1, vector_store=vector_store)
        use_case_v2 = MemoryUseCase(llm_service=llm_v2, vector_store=vector_store)
        
        # Both work because they follow the same interface
        assert use_case_v1.llm_service is llm_v1
        assert use_case_v2.llm_service is llm_v2
    
    def test_with_unittest_mock(self):
        """
        Alternative approach using unittest.mock.Mock.
        """
        # Create mocks using unittest.mock
        mock_llm = Mock(spec=LlmInterface)
        mock_llm.embed.return_value = [[0.1, 0.2, 0.3]]
        mock_llm.generate_response.return_value = '{"facts": ["Test fact"]}'
        
        mock_vector_store = Mock(spec=BaseVectorStore)
        
        # Inject mocks
        use_case = MemoryUseCase(
            llm_service=mock_llm,
            vector_store=mock_vector_store
        )
        
        # Test
        request = CreateMemoryRequest(text="Test message", user_id="user-1")
        use_case.add(request)
        
        # Verify calls
        mock_llm.generate_response.assert_called_once()
        mock_llm.embed.assert_called()


# Integration test example with real container
class TestWithContainer:
    """
    Example of integration testing with the real DI container.
    """
    
    def test_container_provides_dependencies(self):
        """
        Test that the container correctly wires dependencies.
        This is an integration test that uses real implementations.
        """
        from ai_mem.server.infrastructure.container import Container
        
        # Create container
        container = Container()
        
        # Get use case from container
        memory_use_case = container.memory_use_case()
        
        # Verify dependencies are injected
        assert memory_use_case.llm_service is not None
        assert memory_use_case.vector_store is not None
        
        # Verify they are the right types
        from ai_mem.server.infrastructure.service.llm.ollama import OllamaService
        from ai_mem.server.infrastructure.service.vector_store.pgvector import PgVectorStore
        
        assert isinstance(memory_use_case.llm_service, OllamaService)
        assert isinstance(memory_use_case.vector_store, PgVectorStore)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
