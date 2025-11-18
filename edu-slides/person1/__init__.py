"""
Search & Query Specialist Module

This module provides functionality for:
- Query expansion: Turning a single topic into multiple well-phrased queries
- Search orchestration: Using OpenAI's web search to get relevant results
- Result parsing: Extracting structured data from search results
"""

from .collector import collect_raw

__all__ = ['collect_raw']


