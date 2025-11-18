"""
Search Orchestrator Module

Uses OpenAI's responses.create() with web_search tool to perform searches,
handling pagination, retries, and combining results from multiple queries.
"""

import time
from typing import List, Dict, Any
from openai import OpenAI
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.env_config import get_openai_api_key


class SearchOrchestrator:
    """Orchestrates web searches using OpenAI's web search tool."""

    def __init__(self, api_key: str = None):
        """
        Initialize the search orchestrator.
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            try:
                api_key = get_openai_api_key()
                self.client = OpenAI(api_key=api_key)
            except ValueError as e:
                raise ValueError(f"Failed to initialize OpenAI client: {e}") from e

    def search(self, query: str, max_results: int = 5, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a web search using OpenAI's web_search tool.
        """
        for attempt in range(max_retries):
            try:
                results = self._search_with_gpt(query, max_results)
                if results:
                    return results
            except Exception as e:
                print(f"Search attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        return []

    def _search_with_gpt(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Perform a real web search and extract results cleanly.
        Handles pagination if the API supports it.
        """
        try:
            results_list = []
            page_token = None
            
            # Handle pagination - fetch multiple pages if needed
            while len(results_list) < max_results:
                # Prepare request parameters
                request_params = {
                    "model": "gpt-4.1-mini",
                    "tools": [{"type": "web_search"}],
                    "tool_choice": {"type": "web_search"},
                    "input": query
                }
                
                # Add pagination token if available
                if page_token:
                    request_params["page_token"] = page_token
                
                response = self.client.responses.create(**request_params)
                
                # Extract search results from response
                page_results = self._extract_results_from_response(response)
                results_list.extend(page_results)

                # Check for pagination token in response
                page_token = getattr(response, 'next_page_token', None) or getattr(response, 'page_token', None)
                
                # If no more pages or we have enough results, break
                if not page_token or len(results_list) >= max_results:
                    break

            # Return only the top N results, avoiding duplicates
            seen_urls = set()
            unique_results = []
            for result in results_list:
                if result.get("url") and result["url"] not in seen_urls:
                    seen_urls.add(result["url"])
                    unique_results.append(result)
                    if len(unique_results) >= max_results:
                        break

            return unique_results[:max_results]

        except Exception as e:
            print(f"Web search failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_results_from_response(self, response: Any) -> List[Dict[str, Any]]:
        """
        Extract search results from the API response.
        Handles different possible response structures.
        """
        results_list = []
        
        # Structure 1: response.output[].content[].annotations[] with citations
        if hasattr(response, 'output') and response.output:
            for output in response.output:
                if hasattr(output, 'content') and output.content:
                    for content in output.content:
                        # Check annotations for citations
                        if hasattr(content, 'annotations') and content.annotations:
                            # Get content text that might contain snippet information
                            content_text = getattr(content, 'text', None) or getattr(content, 'content', None) or ""
                            
                            for annotation in content.annotations:
                                # Check if annotation is a citation
                                if hasattr(annotation, 'citation') and annotation.citation:
                                    # Try to get snippet from annotation text, content text, or annotation itself
                                    annotation_text = (
                                        getattr(annotation, 'text', None) or
                                        getattr(annotation, 'content', None) or
                                        getattr(annotation, 'quote', None) or
                                        ""
                                    )
                                    # If no annotation text, try to use surrounding content text
                                    if not annotation_text and content_text:
                                        # Use a portion of content text as snippet (first 200 chars)
                                        annotation_text = content_text[:200] if len(content_text) > 200 else content_text
                                    
                                    result = self._format_result(annotation.citation, annotation_text)
                                    if result.get("title") and result.get("url"):
                                        results_list.append(result)
                                
                                # Check if annotation has direct citation fields
                                elif hasattr(annotation, 'url') or hasattr(annotation, 'title'):
                                    # Try to get snippet from annotation text or content text
                                    annotation_text = (
                                        getattr(annotation, 'text', None) or
                                        getattr(annotation, 'content', None) or
                                        getattr(annotation, 'quote', None) or
                                        ""
                                    )
                                    # If no annotation text, try to use surrounding content text
                                    if not annotation_text and content_text:
                                        annotation_text = content_text[:200] if len(content_text) > 200 else content_text
                                    
                                    result = self._format_result(annotation, annotation_text)
                                    if result.get("title") and result.get("url"):
                                        results_list.append(result)
                        
                        # Check for web_search directly in content
                        if hasattr(content, 'web_search') and content.web_search:
                            web_search = content.web_search
                            if hasattr(web_search, 'results') and web_search.results:
                                for item in web_search.results:
                                    result = self._format_result(item)
                                    if result.get("title") and result.get("url"):
                                        results_list.append(result)
                        
                        # Check if content itself has text that could be a snippet
                        if hasattr(content, 'text') and content.text:
                            # Try to extract citations from text annotations
                            pass  # Already handled above
                
                # Check for citations directly in output
                if hasattr(output, 'citations') and output.citations:
                    for citation in output.citations:
                        result = self._format_result(citation)
                        if result.get("title") and result.get("url"):
                            results_list.append(result)
        
        # Structure 2: response.citations[]
        if not results_list and hasattr(response, 'citations') and response.citations:
            for citation in response.citations:
                result = self._format_result(citation)
                if result.get("title") and result.get("url"):
                    results_list.append(result)
        
        # Structure 3: response.results[] or response.search_results[]
        if not results_list:
            for attr_name in ['results', 'search_results', 'web_search_results']:
                if hasattr(response, attr_name):
                    attr_value = getattr(response, attr_name)
                    if isinstance(attr_value, list):
                        for item in attr_value:
                            result = self._format_result(item)
                            if result.get("title") and result.get("url"):
                                results_list.append(result)
                        break
        
        # Structure 4: Direct dict access
        if not results_list and isinstance(response, dict):
            for key in ['results', 'search_results', 'citations', 'web_search']:
                if key in response:
                    items = response[key]
                    if isinstance(items, list):
                        for item in items:
                            # If nested results, extract them
                            if isinstance(item, dict) and 'results' in item:
                                items = item['results']
                            result = self._format_result(item)
                            if result.get("title") and result.get("url"):
                                results_list.append(result)
                        break
        
        return results_list

    def _format_result(self, item: Any, annotation_text: str = "") -> Dict[str, Any]:
        """
        Formats a single SearchResult item safely.
        Extracts title, url, summary, date, and snippet as required.
        Handles both dict and object types.
        
        Args:
            item: The citation or result item to format
            annotation_text: Optional text from annotation that can be used as snippet
        """
        # Helper function to safely get value from dict or object
        def get_value(key: str) -> str:
            if isinstance(item, dict):
                return item.get(key, "") or ""
            else:
                return getattr(item, key, None) or ""
        
        # Try multiple possible field names for each field
        title = (
            get_value("title") or
            get_value("name") or
            ""
        )
        
        url = (
            get_value("url") or
            get_value("link") or
            get_value("uri") or
            ""
        )
        
        # For summary, try multiple field names
        summary = (
            get_value("summary") or
            get_value("description") or
            get_value("abstract") or
            get_value("excerpt") or
            ""
        )
        
        # For date, try multiple field names
        date = (
            get_value("date") or
            get_value("published_date") or
            get_value("publishedDate") or
            get_value("publication_date") or
            get_value("publicationDate") or
            get_value("created_at") or
            get_value("createdAt") or
            ""
        )
        
        # For snippet, prioritize annotation text, then try multiple field names
        snippet = (
            annotation_text or
            get_value("snippet") or
            get_value("description") or
            get_value("summary") or
            get_value("excerpt") or
            get_value("text") or
            get_value("content") or
            ""
        )
        
        # If snippet is still empty but summary has content, use summary
        if not snippet and summary:
            snippet = summary
        
        # Note: We don't copy snippet to summary - they serve different purposes
        # Summary should be a brief overview, snippet is extracted text
        # If the API doesn't provide summary, it remains empty
        
        return {
            "title": title,
            "url": url,
            "summary": summary,
            "date": date,
            "snippet": snippet
        }

    def search_multiple(self, queries: List[str], max_results_per_query: int = 5) -> List[Dict[str, Any]]:
        """
        Perform searches for multiple queries and combine them.
        """
        all_results = []
        seen_urls = set()

        for query in queries:
            results = self.search(query, max_results=max_results_per_query)

            for result in results:
                if result["url"] and result["url"] not in seen_urls:
                    seen_urls.add(result["url"])
                    all_results.append(result)

            time.sleep(0.5)

        return all_results
