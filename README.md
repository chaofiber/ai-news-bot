# TechCrunch News Bot 🤖

An intelligent news aggregation bot that fetches, summarizes, and filters TechCrunch articles based on your interests.

## Features

- **📰 Multi-source fetching**: RSS feed or web scraping
- **🤖 AI Summarization**: Uses Google Gemini to create concise summaries
- **🎯 Interest Filtering**: Customizable filtering based on topics you care about
- **📊 Relevance Scoring**: Intelligent ranking of articles

## Project Structure

```
news-bot/
├── src/
│   ├── scrapers/       # RSS and web scraping modules
│   ├── summarizers/    # AI summarization (Gemini)
│   └── filters/        # Interest-based filtering
├── tests/              # Unit tests
├── config/             # Configuration files
├── data/               # Output data files
└── main.py            # Main entry point
```

## Setup

1. **Install dependencies**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Gemini API**:
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add to `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
```

3. **Customize interests** (optional):
   - Edit `config/interests_config.json`
   - Add your topics, keywords, and priorities

## Usage

### Basic Usage

```bash
# Fetch posts from last 24 hours (RSS)
python main.py

# Use web scraper for more posts
python main.py --scraper

# Fetch posts from last week
python main.py --hours 168 --scraper
```

### With AI Features

```bash
# Summarize posts with Gemini
python main.py --summarize

# Filter by your interests
python main.py --filter

# Full pipeline: fetch, summarize, and filter
python main.py --scraper --summarize --filter

# Save results
python main.py --scraper --filter --save filtered_results.json
```

### Examples

```bash
# Get robotics news from the past week
python main.py --hours 168 --scraper --summarize --filter

# Quick daily digest
python main.py --scraper --filter
```

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_filters.py
```

## Configuration

### Interest Configuration

Edit `config/interests_config.json`:

```json
{
  "interests": [
    {
      "topic": "robotics",
      "keywords": ["robot", "autonomous", "automation"],
      "priority": "high"
    }
  ],
  "exclude_topics": [
    {
      "topic": "social_media",
      "keywords": ["facebook", "twitter"]
    }
  ]
}
```

### Scoring Weights

- **High priority**: 3x weight
- **Title matches**: 2x multiplier
- **Summary matches**: 1.5x multiplier

## Output Files

- `data/techcrunch_posts.json` - Raw fetched posts
- `data/summarized_posts.json` - Posts with AI summaries
- `data/filtered_posts.json` - Filtered relevant posts

## Requirements

- Python 3.8+
- Google Gemini API key
- Internet connection

## License

MIT