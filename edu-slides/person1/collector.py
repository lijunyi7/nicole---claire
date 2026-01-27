"""
Main Collector Module

Combines query expansion, search orchestration, and result parsing
to collect raw search results for a given topic and grade level.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .query_expansion import expand_query
from .search_orchestrator import SearchOrchestrator
from .result_parser import validate_result

# Cache directory - store in the edu-slides directory
CACHE_DIR = Path(__file__).parent.parent


def collect_raw(topic: str, grade: str = None) -> List[Dict[str, Any]]:
    """
    Collect raw search results for a given topic and grade level.
    
    This function:
    1. Expands the topic into multiple well-phrased queries
    2. Performs web searches using OpenAI's web search tool
    3. Parses and combines results from all queries
    4. Returns a JSON list of 15-20 items
    
    Args:
        topic: The topic to search for (e.g., "Photosynthesis")
        grade: Optional grade level (e.g., "5th grade", "high school", "10th")
    
    Returns:
        List of dictionaries, each containing:
        - title: str
        - url: str
        - summary: str
        - date: str
        - snippet: str
    
    Example:
        >>> results = collect_raw("Photosynthesis", "5th grade")
        >>> print(len(results))  # Should be 15-20
        >>> print(results[0]['title'])
    """
    # Generate cache filename
    cache_name = f"cache_{topic.replace(' ', '_').lower()}"
    if grade:
        cache_name += f"_{grade.replace(' ', '_').lower()}"
    cache_name += ".json"
    cache_path = CACHE_DIR / cache_name

    # If cached, load and return (but enrich summaries if missing)
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            print(f"⚡ Loading cached results: {cache_path.name}")
            cached_results = json.load(f)

        if any(not (item.get("summary") or "").strip() for item in cached_results):
            try:
                orchestrator = SearchOrchestrator()
                max_items = int(os.getenv("SUMMARY_MAX_ITEMS", "10"))
                force = os.getenv("SUMMARY_FORCE", "1").lower() not in {"0", "false", "no"}
                if orchestrator.enrich_summaries(
                    cached_results,
                    topic,
                    grade,
                    max_items=max_items,
                    force=force,
                ):
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(cached_results, f, indent=2, ensure_ascii=False)
            except Exception as enrich_err:
                print(f"Warning: failed to enrich cached summaries: {enrich_err}")

        return cached_results

    # Step 1: Expand topic into multiple queries
    print(f"🔍 Expanding queries for topic: {topic}")
    queries = expand_query(topic, grade)
    print(f"   Generated {len(queries)} queries: {queries[:3]}...")
    
    # Step 2: Perform searches using orchestrator
    print(f"🌐 Performing web searches...")
    orchestrator = SearchOrchestrator()
    
    # Calculate how many results per query we need
    target_count = 20
    results_per_query = max(3, target_count // len(queries))
    
    all_results = orchestrator.search_multiple(
        queries, 
        max_results_per_query=results_per_query
    )
    
    print(f"   Found {len(all_results)} total results")
    
    # Step 3: Validate results (already formatted by orchestrator)
    print(f"📝 Validating results...")
    valid_results = [r for r in all_results if validate_result(r)]
    
    # Step 3b: Enrich summaries from source content when missing
    try:
        max_items = int(os.getenv("SUMMARY_MAX_ITEMS", "10"))
        force = os.getenv("SUMMARY_FORCE", "1").lower() not in {"0", "false", "no"}
        orchestrator.enrich_summaries(
            valid_results,
            topic,
            grade,
            max_items=max_items,
            force=force,
        )
    except Exception as enrich_err:
        print(f"Warning: failed to enrich summaries: {enrich_err}")

    # Step 4: Return 15-20 items
    final_results = valid_results[:20]  # Take up to 20
    
    if len(final_results) < 15:
        print(f"⚠️  Warning: Only found {len(final_results)} valid results (target: 15-20)")
    else:
        print(f"✅ Collected {len(final_results)} results")
    
    # Save to cache
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    print(f"💾 Results cached: {cache_path.name}")

    return final_results


def collect_raw_json(topic: str, grade: str = None) -> str:
    """
    Collect raw search results and return as JSON string.
    
    Args:
        topic: The topic to search for
        grade: Optional grade level
    
    Returns:
        JSON string representation of the results
    """
    results = collect_raw(topic, grade)
    return json.dumps(results, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    
    # Require user input
    if len(sys.argv) < 2:
        print("Usage: python -m search.collector <topic> [grade]")
        print("\nExample: python -m search.collector 'Photosynthesis' '5th grade'")
        sys.exit(1)
    
    topic = sys.argv[1]
    grade = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Example usage
    print("=" * 50)
    print("Search & Query Specialist - Test Run")
    print("=" * 50)
    
    results = collect_raw(topic, grade)
    
    print(f"\n📊 Results Summary:")
    print(f"   Topic: {topic}")
    print(f"   Grade: {grade or 'Not specified'}")
    print(f"   Total Results: {len(results)}")
    
    if results:
        print(f"\n📄 Sample Result:")
        print(f"   Title: {results[0].get('title', 'N/A')}")
        print(f"   URL: {results[0].get('url', 'N/A')}")
        print(f"   Summary: {results[0].get('summary', 'N/A')[:100]}...")

