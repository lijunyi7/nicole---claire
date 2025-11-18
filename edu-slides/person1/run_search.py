#!/usr/bin/env python3
"""
Simple script to run the search module.
Usage: python run_search.py [topic] [grade]
"""

import sys
import json
from pathlib import Path

# Add parent directory to path so we can import the search module
sys.path.insert(0, str(Path(__file__).parent.parent))

from search import collect_raw


def main():
    """Main function to run the search collector."""
    
    # Require topic and grade from command line
    if len(sys.argv) < 2:
        print("Usage: python run_search.py <topic> [grade]")
        print("\nExample: python run_search.py 'Photosynthesis' '5th grade'")
        print("Example: python run_search.py 'Fractions'")
        sys.exit(1)
    
    topic = sys.argv[1]
    grade = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 60)
    print("🔍 Search & Query Specialist")
    print("=" * 60)
    print(f"Topic: {topic}")
    if grade:
        print(f"Grade: {grade}")
    print("=" * 60)
    print()
    
    try:
        # Collect results
        results = collect_raw(topic, grade)
        
        # Display summary
        print(f"\n📊 Results Summary:")
        print(f"   Total Results: {len(results)}")
        
        if results:
            print(f"\n📄 Sample Results (first 3):")
            for i, result in enumerate(results[:3], 1):
                print(f"\n   {i}. {result.get('title', 'N/A')}")
                print(f"      URL: {result.get('url', 'N/A')}")
                print(f"      Summary: {result.get('summary', 'N/A')[:80]}...")
        
        print(f"\n✅ Success! Collected {len(results)} results.")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. A .env file in the project root with OPENAI_API_KEY=your_key")
        print("2. Or set the environment variable: export OPENAI_API_KEY=your_key")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


