"""
Query Expansion Module

Turns a single topic into multiple well-phrased queries to get comprehensive search results.
"""

from typing import List
from openai import OpenAI
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.env_config import get_openai_api_key


def expand_query(topic: str, grade: str = None) -> List[str]:
    """
    Expand a single topic into multiple well-phrased queries.
    
    Args:
        topic: The main topic to search for (e.g., "Photosynthesis")
        grade: Optional grade level to tailor queries (e.g., "5th grade", "high school")
    
    Returns:
        List of expanded queries
    """
    try:
        api_key = get_openai_api_key()
        client = OpenAI(api_key=api_key)
        
        # Create a prompt for query expansion
        grade_context = f" for {grade} students" if grade else ""
        prompt = f"""Given the topic "{topic}"{grade_context}, generate 5-7 well-phrased search queries that would help gather comprehensive information about this topic.

The queries should:
- Cover different aspects of the topic (basics, processes, examples, applications)
- Be specific and search-friendly
- Be appropriate for the grade level if specified

Return only the queries, one per line, without numbering or bullets."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a search query expert. Generate well-phrased, specific search queries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        # Parse the response into a list of queries – use exactly what GPT returns
        queries_text = response.choices[0].message.content.strip()
        queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
        # Only use GPT-generated queries; don't inject our own templates
        return queries[:5]  # Limit to 5 queries max
        
    except Exception as e:
        print(f"Warning: Query expansion failed, using minimal fallback: {e}")
        # Minimal, neutral fallback if the API fails hard: just search the topic itself
        return [topic]


