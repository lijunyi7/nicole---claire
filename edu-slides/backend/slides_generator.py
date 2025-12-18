"""
Fake slides generator for Educational Slides Resource Collector
Generates slide content based on ranked educational resources
"""

from typing import List, Dict, Any
from datetime import datetime


def generate_slides(ranked_results: List[Dict[str, Any]], topic: str, grade: str) -> List[Dict[str, Any]]:
    """
    Generate fake slides from ranked educational resources.
    
    Args:
        ranked_results: List of ranked educational resources
        topic: The educational topic
        grade: Grade level
        
    Returns:
        List of slide dictionaries
    """
    slides = []
    
    # Slide 1: Title slide
    slides.append({
        "type": "title",
        "title": f"Introduction to {topic}",
        "content": f"Educational content for {grade} students",
        "image_url": None
    })
    
    # Slide 2: Overview
    if ranked_results:
        overview_points = []
        # Use summaries from top 3 results to create overview
        for i, result in enumerate(ranked_results[:3], 1):
            summary = result.get("summary", "")
            if summary:
                # Take first sentence or first 100 chars
                point = summary.split('.')[0][:100]
                if point:
                    overview_points.append(point + "...")
        
        if not overview_points:
            overview_points = [
                f"{topic} is an important topic in education",
                f"Understanding {topic} helps students learn key concepts",
                f"This presentation covers the basics of {topic}"
            ]
        
        slides.append({
            "type": "overview",
            "title": f"What is {topic}?",
            "content": overview_points[:3],  # Max 3 points
            "image_url": None
        })
    
    # Slide 3-6: Key concepts (using top ranked results)
    concept_count = min(4, len(ranked_results))
    for i in range(concept_count):
        if i < len(ranked_results):
            result = ranked_results[i]
            title = result.get("title", f"Key Concept {i+1}")
            summary = result.get("summary", "")
            
            # Create bullet points from summary
            if summary:
                # Split by sentences and take first 3-4
                sentences = [s.strip() for s in summary.split('.') if s.strip()]
                points = sentences[:4]
            else:
                points = [
                    f"Important aspect of {topic}",
                    f"Key information about {topic}",
                    f"Essential concept related to {topic}"
                ]
            
            slides.append({
                "type": "concept",
                "title": title[:80],  # Limit title length
                "content": points,
                "image_url": None
            })
    
    # Slide 7: Examples (if we have enough results)
    if len(ranked_results) >= 2:
        example_points = []
        for result in ranked_results[:2]:
            source = result.get("source", "Educational Resource")
            title = result.get("title", "")
            if title:
                example_points.append(f"Example from {source}: {title[:60]}")
        
        if example_points:
            slides.append({
                "type": "examples",
                "title": f"Examples and Applications",
                "content": example_points,
                "image_url": None
            })
    
    # Slide 8: Summary
    slides.append({
        "type": "summary",
        "title": "Summary",
        "content": [
            f"We've covered the basics of {topic}",
            f"Key concepts from trusted educational sources",
            f"Continue learning with the resources provided"
        ],
        "image_url": None
    })
    
    # Slide 9: Resources (optional - list top sources)
    if ranked_results:
        resource_points = []
        seen_sources = set()
        for result in ranked_results[:5]:
            source = result.get("source", "")
            url = result.get("url", "")
            if source and source not in seen_sources:
                seen_sources.add(source)
                if url:
                    resource_points.append(f"{source}")
        
        if resource_points:
            slides.append({
                "type": "resources",
                "title": "Additional Resources",
                "content": resource_points,
                "image_url": None
            })
    
    return slides
