"""
Person 1: Search & Query Specialist
Simplified version that collects raw search results from OpenAI web search.
"""

import json
from typing import List, Dict, Any
from openai import OpenAI
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.env_config import get_openai_api_key


class QueryExpander:
    """Expands a single topic into multiple well-phrased queries."""
    
    @staticmethod
    def expand_topic(topic: str, grade: str = "elementary") -> List[str]:
        """
        Turn a single topic into multiple well-phrased queries.
        
        Args:
            topic: The main topic (e.g., "Photosynthesis")
            grade: Grade level (e.g., "elementary", "middle", "high")
            
        Returns:
            List of expanded queries
        """
        # Simple expansion strategy
        base_queries = [
            f"{topic}",
            f"{topic} for {grade} students",
            f"{topic} explained",
            f"{topic} basics",
            f"what is {topic}",
        ]
        
        # Add grade-specific variations
        if grade == "elementary":
            base_queries.extend([
                f"{topic} for kids",
                f"simple {topic}",
            ])
        elif grade == "middle":
            base_queries.extend([
                f"{topic} middle school",
                f"{topic} concepts",
            ])
        elif grade == "high":
            base_queries.extend([
                f"{topic} high school",
                f"{topic} advanced",
            ])
        
        return base_queries[:5]  # Return top 5 queries


class SearchOrchestrator:
    """Orchestrates web searches using OpenAI's web search tool."""
    
    def __init__(self, api_key: str = None):
        """Initialize the search orchestrator."""
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            api_key = get_openai_api_key()
            self.client = OpenAI(api_key=api_key)
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a single web search query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, URL, summary, etc.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": f"Search the web for: {query}. Return educational resources."
                    }
                ],
                tools=[{"type": "web_search"}],
                tool_choice="required",
                max_tokens=2000
            )
            
            # Parse the response
            results = self._parse_search_response(response, query)
            return results[:max_results]
            
        except Exception as e:
            print(f"Error in search for '{query}': {e}")
            return []
    
    def _parse_search_response(self, response, query: str) -> List[Dict[str, Any]]:
        """
        Parse OpenAI web search response into structured format.
        
        Args:
            response: OpenAI API response
            query: Original search query
            
        Returns:
            List of parsed results
        """
        results = []
        
        # Check if tool calls were made
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.type == "web_search":
                    # Extract search results from tool call
                    search_results = tool_call.function.arguments if hasattr(tool_call, 'function') else {}
                    
                    # Parse the results (structure may vary)
                    if isinstance(search_results, dict) and "results" in search_results:
                        for item in search_results["results"]:
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "summary": item.get("snippet", item.get("summary", "")),
                                "date": item.get("date", ""),
                                "source": item.get("domain", ""),
                                "query": query
                            })
        
        # Fallback: if no tool calls, try to extract from message content
        if not results and response.choices[0].message.content:
            # Simple fallback parsing
            content = response.choices[0].message.content
            # This is a simplified version - in production, you'd parse more carefully
            results.append({
                "title": f"Result for: {query}",
                "url": "",
                "summary": content[:200],
                "date": "",
                "source": "",
                "query": query
            })
        
        return results


class RawResultCollector:
    """Main collector that combines query expansion and search."""
    
    def __init__(self, api_key: str = None):
        """Initialize the collector."""
        self.query_expander = QueryExpander()
        self.search_orchestrator = SearchOrchestrator(api_key)
    
    def collect_raw(self, topic: str, grade: str = "elementary") -> List[Dict[str, Any]]:
        """
        Collect raw search results for a topic.
        
        Args:
            topic: The educational topic
            grade: Grade level
            
        Returns:
            List of 15-20 raw search result items
        """
        print(f"Collecting raw results for topic: {topic} (grade: {grade})")
        
        # Expand queries
        queries = self.query_expander.expand_topic(topic, grade)
        print(f"Generated {len(queries)} search queries")
        
        # Search for each query
        all_results = []
        for i, query in enumerate(queries, 1):
            print(f"Searching query {i}/{len(queries)}: {query}")
            results = self.search_orchestrator.search(query, max_results=4)
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        print(f"Collected {len(unique_results)} unique results")
        return unique_results[:20]  # Return up to 20 items


def main():
    """Demo function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python search_collector.py <topic> [grade]")
        print("Example: python search_collector.py 'Photosynthesis' 'elementary'")
        sys.exit(1)
    
    topic = sys.argv[1]
    grade = sys.argv[2] if len(sys.argv) > 2 else "elementary"
    
    collector = RawResultCollector()
    results = collector.collect_raw(topic, grade)
    
    # Save to JSON
    output_file = Path(__file__).parent.parent / "data" / "raw" / f"{topic.replace(' ', '_')}_raw.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(results)} results to: {output_file}")
    print(f"\nSample result:")
    if results:
        print(json.dumps(results[0], indent=2))


if __name__ == "__main__":
    main()
