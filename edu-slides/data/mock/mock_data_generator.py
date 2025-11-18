"""
Mock Data Generator for Person 2 Testing
Generates fake raw search results that match Person 1's output format.
"""

import json
import random
from typing import List, Dict, Any
from pathlib import Path


# Trusted educational domains
TRUSTED_DOMAINS = [
    "khanacademy.org",
    "wikipedia.org",
    "openstax.org",
    "ck12.org",
    "edu.gov",
    "nasa.gov",
    "nationalgeographic.org",
    "britannica.com",
    "pbs.org",
    "ted.com",
]

# Untrusted/ad domains
UNTRUSTED_DOMAINS = [
    "example-ads.com",
    "spam-site.net",
    "clickbait.org",
]

# Content types
CONTENT_TYPES = ["video", "pdf", "text", "interactive"]


def generate_mock_result(
    topic: str,
    query: str,
    is_trusted: bool = True,
    content_type: str = None
) -> Dict[str, Any]:
    """
    Generate a single mock search result.
    
    Args:
        topic: The main topic
        query: The search query used
        is_trusted: Whether to use a trusted domain
        content_type: Type of content (video, pdf, text, interactive)
        
    Returns:
        Mock search result dictionary
    """
    if content_type is None:
        content_type = random.choice(CONTENT_TYPES)
    
    # Choose domain
    if is_trusted:
        domain = random.choice(TRUSTED_DOMAINS)
    else:
        domain = random.choice(UNTRUSTED_DOMAINS)
    
    # Generate URL
    url = f"https://{domain}/{topic.lower().replace(' ', '-')}/{random.randint(1000, 9999)}"
    
    # Generate title
    title_variations = [
        f"{topic}: Complete Guide",
        f"Understanding {topic}",
        f"{topic} Explained Simply",
        f"Introduction to {topic}",
        f"{topic} Basics for Students",
        f"Learn {topic} Step by Step",
    ]
    title = random.choice(title_variations)
    
    # Generate summary
    summary_templates = [
        f"This comprehensive resource covers all aspects of {topic}, from basic concepts to advanced applications.",
        f"Learn about {topic} through interactive examples and clear explanations designed for students.",
        f"Explore {topic} with detailed explanations, visual aids, and practice exercises.",
        f"A beginner-friendly guide to {topic} that breaks down complex concepts into easy-to-understand sections.",
    ]
    summary = random.choice(summary_templates)
    
    # Generate date (recent dates get higher scores)
    year = random.choice([2024, 2023, 2022, 2021, 2020])
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date = f"{year}-{month:02d}-{day:02d}"
    
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "date": date,
        "source": domain,
        "query": query,
        "content_type": content_type,  # Added for Person 2 scoring
    }


def generate_mock_raw_data(
    topic: str,
    grade: str = "elementary",
    num_results: int = 18,
    trusted_ratio: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Generate mock raw data matching Person 1's output format.
    
    Args:
        topic: The educational topic
        grade: Grade level
        num_results: Number of results to generate (15-20)
        trusted_ratio: Ratio of trusted vs untrusted domains (0.0-1.0)
        
    Returns:
        List of mock search results
    """
    # Generate queries (similar to Person 1)
    queries = [
        f"{topic}",
        f"{topic} for {grade} students",
        f"{topic} explained",
        f"{topic} basics",
        f"what is {topic}",
    ]
    
    results = []
    trusted_count = int(num_results * trusted_ratio)
    
    for i in range(num_results):
        query = random.choice(queries)
        is_trusted = i < trusted_count
        content_type = random.choice(CONTENT_TYPES)
        
        result = generate_mock_result(topic, query, is_trusted, content_type)
        results.append(result)
    
    # Shuffle to mix trusted and untrusted
    random.shuffle(results)
    
    return results


def save_mock_data(topic: str, grade: str = "elementary", output_dir: Path = None):
    """
    Generate and save mock data to JSON file.
    
    Args:
        topic: The educational topic
        grade: Grade level
        output_dir: Output directory (defaults to data/raw/)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "raw"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate mock data
    mock_data = generate_mock_raw_data(topic, grade, num_results=18)
    
    # Save to file
    filename = f"{topic.replace(' ', '_').lower()}_raw.json"
    output_file = output_dir / filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(mock_data)} mock results")
    print(f"Saved to: {output_file}")
    print(f"\nSample result:")
    print(json.dumps(mock_data[0], indent=2))
    
    return output_file


def main():
    """Demo function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mock_data_generator.py <topic> [grade]")
        print("Example: python mock_data_generator.py 'Photosynthesis' 'elementary'")
        sys.exit(1)
    
    topic = sys.argv[1]
    grade = sys.argv[2] if len(sys.argv) > 2 else "elementary"
    
    save_mock_data(topic, grade)


if __name__ == "__main__":
    main()
