"""
Raw Result Parser Module

Extracts title, URL, summary, date, and snippet from OpenAI search output
and formats them into a structured JSON list.
"""

from typing import List, Dict, Any


def parse_result(item: Any) -> Dict[str, Any]:
    """
    Parse a single search result item into a structured dictionary.
    
    Args:
        item: Raw result item from OpenAI (could be dict or object)
    
    Returns:
        Parsed result dictionary with title, url, summary, date, snippet
    """
    # Helper function to safely get value from dict or object
    def get_value(key: str, default: str = "") -> str:
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
    
    # For snippet, try multiple field names
    snippet = (
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


def parse_results(raw_results: List[Any]) -> List[Dict[str, Any]]:
    """
    Parse a list of raw search results into structured JSON format.
    
    Args:
        raw_results: List of raw result items from OpenAI
    
    Returns:
        List of parsed result dictionaries
    """
    parsed = []
    seen_urls = set()
    
    for item in raw_results:
        result = parse_result(item)
        
        # Only include results with at least a title and URL
        url = result.get("url", "")
        if result.get("title") and url and url not in seen_urls:
            seen_urls.add(url)
            parsed.append(result)
    
    return parsed


def validate_result(result: Dict[str, Any]) -> bool:
    """
    Validate that a result has minimum required fields.
    
    Args:
        result: Result dictionary to validate
    
    Returns:
        True if result is valid, False otherwise
    """
    return bool(result.get("title") and result.get("url"))


