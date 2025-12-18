"""
Person 2: Filtering & Ranking Specialist
Cleans and prioritizes search results from Person 1.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import re


# Trusted educational domains (allow-list)
TRUSTED_DOMAINS = {
    "khanacademy.org": 1.0,
    "wikipedia.org": 0.9,
    "openstax.org": 1.0,
    "ck12.org": 0.9,
    "edu.gov": 1.0,
    "nasa.gov": 0.95,
    "nationalgeographic.org": 0.9,
    "britannica.com": 0.85,
    "pbs.org": 0.9,
    "ted.com": 0.85,
    "crashcourse.com": 0.85,
    "coursera.org": 0.8,
    "edx.org": 0.8,
    "mit.edu": 0.95,
    "stanford.edu": 0.95,
}

# Content type preferences
CONTENT_TYPE_SCORES = {
    "video": 0.3,
    "interactive": 0.25,
    "text": 0.2,
    "pdf": 0.15,
}


class DomainFilter:
    """Filters results based on trusted domains."""
    
    def __init__(self, trusted_domains: Dict[str, float] = None):
        """
        Initialize domain filter.
        
        Args:
            trusted_domains: Dictionary mapping domains to trust scores
        """
        self.trusted_domains = trusted_domains or TRUSTED_DOMAINS
    
    def is_trusted(self, url: str) -> bool:
        """
        Check if a URL belongs to a trusted domain.
        
        Args:
            url: URL to check
            
        Returns:
            True if trusted, False otherwise
        """
        if not url:
            return False
        
        # Extract domain from URL
        domain = self._extract_domain(url)

        # Treat any .edu or .gov domain as trusted (e.g., school.edu, district.k12.ca.us)
        if domain.endswith(".edu") or domain.endswith(".gov") or domain.endswith(".org"):
            return True
        
        # Check if domain is in explicit trusted list
        return domain in self.trusted_domains
    
    def get_trust_score(self, url: str) -> float:
        """
        Get trust score for a domain.
        
        Args:
            url: URL to check
            
        Returns:
            Trust score (0.0-1.0), 0.0 if not trusted
        """
        if not url:
            return 0.0
        
        domain = self._extract_domain(url)

        # .edu / .gov domains get top trust if not explicitly listed
        if domain.endswith(".edu") or domain.endswith(".gov"):
            return self.trusted_domains.get(domain, 1.0)

        return self.trusted_domains.get(domain, 0.0)
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ""
        
        # Remove protocol
        url = url.replace("https://", "").replace("http://", "")
        
        # Get domain (first part before /)
        domain = url.split("/")[0]
        
        # Remove www.
        domain = domain.replace("www.", "")
        
        return domain.lower()


class DuplicateRemover:
    """Removes duplicate results."""
    
    @staticmethod
    def remove_duplicates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate items based on URL.
        
        Args:
            items: List of search results
            
        Returns:
            List with duplicates removed
        """
        seen_urls = set()
        unique_items = []
        
        for item in items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)
        
        return unique_items
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """
        Normalize title for comparison.
        
        Args:
            title: Title string
            
        Returns:
            Normalized title
        """
        if not title:
            return ""
        
        # Convert to lowercase, remove extra spaces
        normalized = re.sub(r'\s+', ' ', title.lower().strip())
        return normalized


class ScoringFunction:
    """Calculates scores for ranking results."""
    
    def __init__(self, domain_filter: DomainFilter):
        """
        Initialize scoring function.
        
        Args:
            domain_filter: Domain filter instance
        """
        self.domain_filter = domain_filter
    
    def calculate_score(
        self,
        item: Dict[str, Any],
        topic: str,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate composite score for an item.
        
        Formula: score = 0.5*similarity + 0.3*trust + 0.1*recency + 0.1*format
        
        Args:
            item: Search result item
            topic: Original topic
            weights: Custom weights for scoring components
            
        Returns:
            Composite score (0.0-1.0)
        """
        if weights is None:
            weights = {
                "similarity": 0.5,
                "trust": 0.3,
                "recency": 0.1,
                "format": 0.1
            }
        
        # Calculate components
        similarity_score = self._keyword_similarity(item, topic)
        trust_score = self.domain_filter.get_trust_score(item.get("url", ""))
        recency_score = self._recency_bonus(item.get("date", ""))
        format_score = self._content_type_bonus(item.get("content_type", "text"))
        
        # Weighted sum
        total_score = (
            weights["similarity"] * similarity_score +
            weights["trust"] * trust_score +
            weights["recency"] * recency_score +
            weights["format"] * format_score
        )
        
        return round(total_score, 4)
    
    def _keyword_similarity(self, item: Dict[str, Any], topic: str) -> float:
        """
        Calculate keyword similarity between topic and item title/summary.
        
        Args:
            item: Search result item
            topic: Original topic
            
        Returns:
            Similarity score (0.0-1.0)
        """
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        topic_lower = topic.lower()
        
        # Split topic into words
        topic_words = set(topic_lower.split())
        
        # Count matches in title
        title_words = set(title.split())
        title_matches = len(topic_words.intersection(title_words))
        title_score = title_matches / len(topic_words) if topic_words else 0.0
        
        # Count matches in summary (weighted less)
        summary_words = set(summary.split())
        summary_matches = len(topic_words.intersection(summary_words))
        summary_score = (summary_matches / len(topic_words) * 0.5) if topic_words else 0.0
        
        # Combined score (title weighted more)
        similarity = min(1.0, title_score * 0.7 + summary_score * 0.3)
        
        return similarity
    
    def _recency_bonus(self, date_str: str) -> float:
        """
        Calculate recency bonus based on date.
        
        Args:
            date_str: Date string (YYYY-MM-DD format)
            
        Returns:
            Recency score (0.0-1.0)
        """
        if not date_str:
            return 0.5  # Neutral score for missing dates
        
        try:
            item_date = datetime.strptime(date_str, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Calculate days difference
            days_diff = (current_date - item_date).days
            
            # Score: 1.0 for current year, decreasing for older years
            if days_diff < 365:
                return 1.0
            elif days_diff < 730:
                return 0.8
            elif days_diff < 1095:
                return 0.6
            else:
                return 0.4
        except:
            return 0.5  # Neutral for invalid dates
    
    def _content_type_bonus(self, content_type: str) -> float:
        """
        Calculate bonus based on content type preference.
        
        Args:
            content_type: Type of content (video, pdf, text, interactive)
            
        Returns:
            Format score (0.0-1.0)
        """
        return CONTENT_TYPE_SCORES.get(content_type.lower(), 0.15)


class TopNSelector:
    """Selects top N results after ranking."""
    
    @staticmethod
    def select_top_n(
        items: List[Dict[str, Any]],
        n: int = 10,
        ensure_diversity: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Select top N items, ensuring source diversity.
        
        Args:
            items: List of scored items
            n: Number of items to select
            ensure_diversity: Whether to ensure diverse sources
            
        Returns:
            Top N items
        """
        # Sort by score (descending)
        sorted_items = sorted(items, key=lambda x: x.get("score", 0.0), reverse=True)
        
        if not ensure_diversity:
            return sorted_items[:n]
        
        # Ensure diversity by limiting items per domain
        selected = []
        domain_count = {}
        max_per_domain = max(2, n // 5)  # At most 2 items per domain for top 10
        
        for item in sorted_items:
            if len(selected) >= n:
                break
            
            domain = DomainFilter._extract_domain(item.get("url", ""))
            domain_count[domain] = domain_count.get(domain, 0)
            
            if domain_count[domain] < max_per_domain:
                selected.append(item)
                domain_count[domain] += 1
        
        # Fill remaining slots if needed
        if len(selected) < n:
            for item in sorted_items:
                if len(selected) >= n:
                    break
                if item not in selected:
                    selected.append(item)
        
        return selected[:n]


def filter_and_rank(
    items_raw: List[Dict[str, Any]],
    topic: str,
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Main function: Filter and rank raw search results.
    
    Args:
        items_raw: Raw search results from Person 1
        topic: Original topic
        top_n: Number of top results to return
        
    Returns:
        Clean, ranked list with score field
    """
    # Step 1: Domain filtering (keep only trusted domains)
    domain_filter = DomainFilter()
    trusted_items = [
        item for item in items_raw
        if domain_filter.is_trusted(item.get("url", ""))
    ]
    
    print(f"Filtered: {len(items_raw)} -> {len(trusted_items)} trusted items")
    
    # Step 2: Remove duplicates
    duplicate_remover = DuplicateRemover()
    unique_items = duplicate_remover.remove_duplicates(trusted_items)
    
    print(f"Deduplicated: {len(trusted_items)} -> {len(unique_items)} unique items")
    
    # Step 3: Calculate scores
    scoring = ScoringFunction(domain_filter)
    scored_items = []
    for item in unique_items:
        score = scoring.calculate_score(item, topic)
        item["score"] = score
        scored_items.append(item)
    
    # Step 4: Select top N
    selector = TopNSelector()
    top_items = selector.select_top_n(scored_items, n=top_n, ensure_diversity=True)
    
    print(f"Selected top {len(top_items)} items")
    
    return top_items


def main():
    """Demo function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python filter_ranker.py <input_json> [topic] [top_n]")
        print("Example: python filter_ranker.py data/raw/photosynthesis_raw.json 'Photosynthesis' 10")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    topic = sys.argv[2] if len(sys.argv) > 2 else "Photosynthesis"
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    # Load raw data
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_items = json.load(f)
    
    print(f"Loaded {len(raw_items)} raw items from: {input_file}")
    print(f"Topic: {topic}")
    print(f"Selecting top {top_n} results\n")
    
    # Filter and rank
    ranked_items = filter_and_rank(raw_items, topic, top_n)
    
    # Save results
    output_file = input_file.parent / f"{input_file.stem}_ranked.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ranked_items, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(ranked_items)} ranked items to: {output_file}")
    print(f"\nTop 3 results:")
    for i, item in enumerate(ranked_items[:3], 1):
        print(f"\n{i}. {item.get('title', 'N/A')}")
        print(f"   URL: {item.get('url', 'N/A')}")
        print(f"   Score: {item.get('score', 0.0):.4f}")
        print(f"   Source: {item.get('source', 'N/A')}")


if __name__ == "__main__":
    main()
