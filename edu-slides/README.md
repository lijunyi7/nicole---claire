# Educational Slides Resource Collector

A three-person team project for collecting, filtering, and ranking educational resources for slide generation.

## Project Structure

```
edu-slides/
├─ person1/              # Search & Query Specialist
│  └─ search_collector.py
├─ person2/              # Filtering & Ranking Specialist (YOUR TASK)
│  └─ filter_ranker.py
├─ person3/              # Caching & API Integration (Future)
├─ config/
│  └─ env_config.py      # Environment configuration
├─ data/
│  ├─ raw/               # Raw search results from Person 1
│  └─ mock/              # Mock data generator for testing
└─ requirements.txt
```

## Person 1: Search & Query Specialist

**Status**: ✅ Simplified version implemented

**Function**: `collect_raw(topic, grade) -> List[Dict]`

Collects 15-20 raw search results from OpenAI web search.

### Usage:
```bash
python person1/search_collector.py "Photosynthesis" "elementary"
```

**Output**: Saves to `data/raw/{topic}_raw.json`

## Person 2: Filtering & Ranking Specialist (YOUR TASK)

**Status**: ✅ Complete implementation provided

**Function**: `filter_and_rank(items_raw, topic, top_n=10) -> List[Dict]`

Filters and ranks results using:
- Domain filtering (trusted OER sites only)
- Duplicate removal
- Scoring formula: `0.5*similarity + 0.3*trust + 0.1*recency + 0.1*format`
- Top-N selection with source diversity

### Usage:
```bash
python person2/filter_ranker.py data/raw/photosynthesis_raw.json "Photosynthesis" 10
```

**Output**: Saves to `data/raw/{topic}_raw_ranked.json`

## Testing Person 2 Without Person 1

Use the mock data generator to test Person 2's functionality:

```bash
# Generate mock data
python data/mock/mock_data_generator.py "Photosynthesis" "elementary"

# This creates: data/raw/photosynthesis_raw.json

# Test Person 2's filtering
python person2/filter_ranker.py data/raw/photosynthesis_raw.json "Photosynthesis" 10
```

## Data Format

### Person 1 Output (Raw Results):
```json
[
  {
    "title": "Photosynthesis Explained",
    "url": "https://khanacademy.org/...",
    "summary": "Learn about photosynthesis...",
    "date": "2024-01-15",
    "source": "khanacademy.org",
    "query": "Photosynthesis",
    "content_type": "video"
  }
]
```

### Person 2 Output (Ranked Results):
```json
[
  {
    "title": "Photosynthesis Explained",
    "url": "https://khanacademy.org/...",
    "summary": "Learn about photosynthesis...",
    "date": "2024-01-15",
    "source": "khanacademy.org",
    "query": "Photosynthesis",
    "content_type": "video",
    "score": 0.8523
  }
]
```

## Scoring Formula

Each result gets a composite score:

```
score = 0.5 * similarity + 0.3 * trust + 0.1 * recency + 0.1 * format
```

- **Similarity** (0.5): Keyword match between topic and title/summary
- **Trust** (0.3): Domain trust score (Khan Academy = 1.0, Wikipedia = 0.9, etc.)
- **Recency** (0.1): Date-based bonus (recent = higher score)
- **Format** (0.1): Content type preference (video > interactive > text > pdf)

## Trusted Domains

The system filters to only trusted educational domains:
- Khan Academy, OpenStax, CK-12
- Wikipedia, Britannica
- Government sites (.edu, .gov)
- PBS, TED, National Geographic
- And more...

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY
   ```

3. **Test with mock data:**
   ```bash
   python data/mock/mock_data_generator.py "Photosynthesis" "elementary"
   python person2/filter_ranker.py data/raw/photosynthesis_raw.json "Photosynthesis"
   ```

## Next Steps

- **Person 3**: Will create FastAPI endpoint that calls Person 1 → Person 2 pipeline
- **Integration**: Connect all three modules together
- **Caching**: Add Redis/local cache for repeated queries
- **Logging**: Track API costs and performance metrics

## Notes

- Person 1's implementation is simplified but functional
- Person 2 is fully implemented and ready to use
- Mock data generator allows testing Person 2 independently
- All modules are designed to work together seamlessly
