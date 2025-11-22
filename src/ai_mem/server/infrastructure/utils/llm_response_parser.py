#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 22, 2025 11:48:21$"

import json
import re
from typing import Any, Optional


def extract_json_from_response(response: str) -> Optional[dict[str, Any]]:
    """
    Extract and parse JSON from LLM response that may contain extra text.
    
    LLM responses often include explanatory text before or after the JSON.
    This function finds and extracts the JSON portion.
    
    Examples:
        >>> extract_json_from_response('{"facts": ["fact1"]}')
        {'facts': ['fact1']}
        
        >>> extract_json_from_response('Here is the output:\\n{"facts": ["fact1"]}')
        {'facts': ['fact1']}
        
        >>> extract_json_from_response('Output: {"facts": []}\\nDone!')
        {'facts': []}
    
    Args:
        response: Raw response string from LLM
        
    Returns:
        Parsed JSON as dictionary, or None if no valid JSON found
        
    Raises:
        ValueError: If JSON is found but invalid
    """
    if not response or not isinstance(response, str):
        return None
    
    # Strategy 1: Try to parse the entire response as JSON
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Find JSON object using regex
    # Look for content between { and } (handles nested objects)
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.finditer(json_pattern, response, re.DOTALL)
    
    for match in matches:
        try:
            json_str = match.group(0)
            return json.loads(json_str)
        except json.JSONDecodeError:
            continue
    
    # Strategy 3: Look for JSON array
    array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
    matches = re.finditer(array_pattern, response, re.DOTALL)
    
    for match in matches:
        try:
            json_str = match.group(0)
            return json.loads(json_str)
        except json.JSONDecodeError:
            continue
    
    # No valid JSON found
    return None


def extract_json_with_fallback(
    response: str,
    fallback: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Extract JSON from response with a fallback value.
    
    Args:
        response: Raw response string from LLM
        fallback: Default value if no JSON found (default: empty dict)
        
    Returns:
        Parsed JSON or fallback value
    """
    if fallback is None:
        fallback = {}
    
    result = extract_json_from_response(response)
    return result if result is not None else fallback


def clean_llm_response(response: str) -> str:
    """
    Clean LLM response by removing common prefixes and suffixes.
    
    Args:
        response: Raw response from LLM
        
    Returns:
        Cleaned response string
    """
    if not response:
        return ""
    
    # Remove common prefixes
    prefixes = [
        "Output:",
        "Result:",
        "Here is the output:",
        "Here's the result:",
        "The output is:",
    ]
    
    cleaned = response.strip()
    for prefix in prefixes:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()
            break
    
    # Remove common suffixes
    suffixes = [
        "Done!",
        "Complete!",
        "Finished!",
    ]
    
    for suffix in suffixes:
        if cleaned.lower().endswith(suffix.lower()):
            cleaned = cleaned[:-len(suffix)].strip()
            break
    
    return cleaned


def parse_facts_from_response(response: str) -> list[str]:
    """
    Parse facts array from LLM response.
    
    Specifically designed for fact extraction responses.
    
    Args:
        response: Raw response from LLM
        
    Returns:
        List of facts, or empty list if none found
    """
    json_data = extract_json_from_response(response)
    
    if json_data is None:
        return []
    
    # Try different possible keys
    for key in ["facts", "fact", "items", "results"]:
        if key in json_data:
            facts = json_data[key]
            if isinstance(facts, list):
                return [str(fact) for fact in facts if fact]
            elif isinstance(facts, str):
                return [facts] if facts else []
    
    return []
