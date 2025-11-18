"""
Quick test script for Person 2's filtering and ranking functionality.
Uses mock data so you can test without Person 1's API calls.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from data.mock.mock_data_generator import save_mock_data
from person2.filter_ranker import filter_and_rank
import json


def test_person2(topic: str = "Photosynthesis", grade: str = "elementary", top_n: int = 10):
    """
    Test Person 2's filtering and ranking with mock data.
    
    Args:
        topic: Educational topic
        grade: Grade level
        top_n: Number of top results to return
    """
    print("=" * 60)
    print("TESTING PERSON 2: Filtering & Ranking")
    print("=" * 60)
    print(f"Topic: {topic}")
    print(f"Grade: {grade}")
    print(f"Top N: {top_n}\n")
    
    # Step 1: Generate mock data (simulating Person 1's output)
    print("Step 1: Generating mock data (simulating Person 1)...")
    output_file = save_mock_data(topic, grade)
    
    # Step 2: Load the mock data
    print(f"\nStep 2: Loading raw data from {output_file}...")
    with open(output_file, 'r', encoding='utf-8') as f:
        raw_items = json.load(f)
    
    print(f"Loaded {len(raw_items)} raw items\n")
    
    # Step 3: Test Person 2's filtering and ranking
    print("Step 3: Running Person 2's filter_and_rank()...")
    print("-" * 60)
    ranked_items = filter_and_rank(raw_items, topic, top_n)
    
    # Step 4: Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nTop {len(ranked_items)} ranked results:\n")
    
    for i, item in enumerate(ranked_items, 1):
        print(f"{i}. {item.get('title', 'N/A')}")
        print(f"   URL: {item.get('url', 'N/A')}")
        print(f"   Score: {item.get('score', 0.0):.4f}")
        print(f"   Source: {item.get('source', 'N/A')}")
        print(f"   Type: {item.get('content_type', 'N/A')}")
        print()
    
    # Step 5: Save ranked results
    ranked_output = output_file.parent / f"{output_file.stem}_ranked.json"
    with open(ranked_output, 'w', encoding='utf-8') as f:
        json.dump(ranked_items, f, indent=2, ensure_ascii=False)
    
    print(f"Saved ranked results to: {ranked_output}")
    print("\n✅ Person 2 test completed successfully!")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Person 2's filtering and ranking")
    parser.add_argument("topic", nargs="?", default="Photosynthesis", help="Educational topic")
    parser.add_argument("--grade", default="elementary", help="Grade level")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top results")
    
    args = parser.parse_args()
    
    test_person2(args.topic, args.grade, args.top_n)


if __name__ == "__main__":
    main()
