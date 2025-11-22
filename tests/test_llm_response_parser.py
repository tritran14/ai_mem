#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 22, 2025 11:48:21$"

import pytest

from ai_mem.server.infrastructure.utils.llm_response_parser import (
    extract_json_from_response,
    extract_json_with_fallback,
    clean_llm_response,
    parse_facts_from_response,
)


class TestExtractJsonFromResponse:
    """Test JSON extraction from LLM responses."""
    
    def test_extract_pure_json(self):
        """Test extraction from pure JSON response."""
        response = '{"facts": ["fact1", "fact2"]}'
        result = extract_json_from_response(response)
        assert result == {"facts": ["fact1", "fact2"]}
    
    def test_extract_json_with_prefix(self):
        """Test extraction when JSON has text prefix."""
        response = 'Here is the output:\n{"facts": ["fact1"]}'
        result = extract_json_from_response(response)
        assert result == {"facts": ["fact1"]}
    
    def test_extract_json_with_suffix(self):
        """Test extraction when JSON has text suffix."""
        response = '{"facts": ["fact1"]}\nDone!'
        result = extract_json_from_response(response)
        assert result == {"facts": ["fact1"]}
    
    def test_extract_json_with_prefix_and_suffix(self):
        """Test extraction when JSON is surrounded by text."""
        response = 'Output: {"facts": ["fact1"]}\nComplete!'
        result = extract_json_from_response(response)
        assert result == {"facts": ["fact1"]}
    
    def test_extract_empty_facts(self):
        """Test extraction of empty facts array."""
        response = 'Since the input is not clear, I will return an empty list.\n\nOutput: {"facts": []}'
        result = extract_json_from_response(response)
        assert result == {"facts": []}
    
    def test_extract_nested_json(self):
        """Test extraction of nested JSON objects."""
        response = '{"facts": [{"text": "fact1", "confidence": 0.9}]}'
        result = extract_json_from_response(response)
        assert result == {"facts": [{"text": "fact1", "confidence": 0.9}]}
    
    def test_extract_json_array(self):
        """Test extraction of JSON array."""
        response = 'Result: ["fact1", "fact2", "fact3"]'
        result = extract_json_from_response(response)
        assert result == ["fact1", "fact2", "fact3"]
    
    def test_no_json_found(self):
        """Test when no JSON is present."""
        response = "This is just plain text without any JSON"
        result = extract_json_from_response(response)
        assert result is None
    
    def test_empty_string(self):
        """Test with empty string."""
        result = extract_json_from_response("")
        assert result is None
    
    def test_none_input(self):
        """Test with None input."""
        result = extract_json_from_response(None)
        assert result is None
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        response = '  \n  {"facts": ["fact1"]}  \n  '
        result = extract_json_from_response(response)
        assert result == {"facts": ["fact1"]}
    
    def test_multiple_json_objects(self):
        """Test when multiple JSON objects are present (returns first valid)."""
        response = '{"invalid": } {"facts": ["fact1"]}'
        result = extract_json_from_response(response)
        assert result == {"facts": ["fact1"]}


class TestExtractJsonWithFallback:
    """Test JSON extraction with fallback values."""
    
    def test_extract_with_default_fallback(self):
        """Test fallback to empty dict when no JSON found."""
        response = "No JSON here"
        result = extract_json_with_fallback(response)
        assert result == {}
    
    def test_extract_with_custom_fallback(self):
        """Test fallback to custom value."""
        response = "No JSON here"
        fallback = {"facts": []}
        result = extract_json_with_fallback(response, fallback)
        assert result == {"facts": []}
    
    def test_extract_success_ignores_fallback(self):
        """Test that fallback is not used when JSON is found."""
        response = '{"facts": ["fact1"]}'
        fallback = {"facts": []}
        result = extract_json_with_fallback(response, fallback)
        assert result == {"facts": ["fact1"]}


class TestCleanLlmResponse:
    """Test LLM response cleaning."""
    
    def test_remove_output_prefix(self):
        """Test removal of 'Output:' prefix."""
        response = "Output: some content"
        result = clean_llm_response(response)
        assert result == "some content"
    
    def test_remove_result_prefix(self):
        """Test removal of 'Result:' prefix."""
        response = "Result: some content"
        result = clean_llm_response(response)
        assert result == "some content"
    
    def test_remove_done_suffix(self):
        """Test removal of 'Done!' suffix."""
        response = "some content Done!"
        result = clean_llm_response(response)
        assert result == "some content"
    
    def test_case_insensitive_cleaning(self):
        """Test that cleaning is case-insensitive."""
        response = "output: some content"
        result = clean_llm_response(response)
        assert result == "some content"
    
    def test_no_cleaning_needed(self):
        """Test when no cleaning is needed."""
        response = "some content"
        result = clean_llm_response(response)
        assert result == "some content"
    
    def test_empty_string(self):
        """Test with empty string."""
        result = clean_llm_response("")
        assert result == ""


class TestParseFactsFromResponse:
    """Test fact parsing from LLM responses."""
    
    def test_parse_facts_array(self):
        """Test parsing facts from standard response."""
        response = '{"facts": ["fact1", "fact2", "fact3"]}'
        result = parse_facts_from_response(response)
        assert result == ["fact1", "fact2", "fact3"]
    
    def test_parse_empty_facts(self):
        """Test parsing empty facts array."""
        response = '{"facts": []}'
        result = parse_facts_from_response(response)
        assert result == []
    
    def test_parse_facts_with_extra_text(self):
        """Test parsing facts when response has extra text."""
        response = 'Since the input is not clear, I will return an empty list.\n\nOutput: {"facts": []}'
        result = parse_facts_from_response(response)
        assert result == []
    
    def test_parse_facts_with_different_key(self):
        """Test parsing when using alternative key names."""
        response = '{"items": ["item1", "item2"]}'
        result = parse_facts_from_response(response)
        assert result == ["item1", "item2"]
    
    def test_parse_single_fact_as_string(self):
        """Test parsing when fact is a string instead of array."""
        response = '{"facts": "single fact"}'
        result = parse_facts_from_response(response)
        assert result == ["single fact"]
    
    def test_parse_no_json(self):
        """Test parsing when no JSON is present."""
        response = "No JSON here"
        result = parse_facts_from_response(response)
        assert result == []
    
    def test_parse_filters_empty_facts(self):
        """Test that empty strings are filtered out."""
        response = '{"facts": ["fact1", "", "fact2", null, "fact3"]}'
        result = parse_facts_from_response(response)
        assert result == ["fact1", "fact2", "fact3"]
    
    def test_parse_converts_to_string(self):
        """Test that non-string facts are converted to strings."""
        response = '{"facts": [123, true, "text"]}'
        result = parse_facts_from_response(response)
        assert result == ["123", "True", "text"]
    
    def test_real_world_example_1(self):
        """Test with real LLM response example."""
        response = '''Since the input is not clear or grammatically correct, I will return an empty list.

Output: {"facts" : []}'''
        result = parse_facts_from_response(response)
        assert result == []
    
    def test_real_world_example_2(self):
        """Test with real LLM response with facts."""
        response = '''Here are the extracted facts:

Output: {"facts": ["User loves programming in Python", "User is learning AI"]}

Done!'''
        result = parse_facts_from_response(response)
        assert result == ["User loves programming in Python", "User is learning AI"]


class TestIntegration:
    """Integration tests for the parser utilities."""
    
    def test_end_to_end_parsing(self):
        """Test complete parsing flow."""
        # Simulate real LLM response
        llm_response = '''I've analyzed the input and extracted the following facts:

Output: {"facts": ["User is a software engineer", "User works with Python"]}

The extraction is complete.'''
        
        # Parse facts
        facts = parse_facts_from_response(llm_response)
        
        # Verify
        assert len(facts) == 2
        assert "User is a software engineer" in facts
        assert "User works with Python" in facts
    
    def test_graceful_degradation(self):
        """Test that parser degrades gracefully with malformed input."""
        malformed_responses = [
            "",
            None,
            "Just text",
            '{"invalid json}',
            '{"facts": null}',
        ]
        
        for response in malformed_responses:
            result = parse_facts_from_response(response)
            assert isinstance(result, list)
            assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
