# LinkedIn Comment Automation

Automate LinkedIn feed scraping, post analysis, and comment generation while maintaining an authentic voice.

## Overview

This system enables you to:

1. **Scrape LinkedIn posts** from your feed
2. **Analyze post content** using AI (categories, summaries)
3. **Generate personalized comment suggestions** based on your persona
4. **Work in isolated, testable phases** to validate each step

## Features

- 🚀 Modern Python 3.11+ with Poetry
- 🤖 Google Gemini 2.5 Flash integration for AI analysis
- 🌐 Selenium-based browser automation
- 💾 Cookie-based session persistence
- 📊 Structured data storage (JSON, Markdown)
- 🔄 Isolated, testable components
- 📝 Comprehensive logging

## Quick Start

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Chrome browser and ChromeDriver

### Setup

1. **Clone and setup**:
   ```bash
   cd linkedin-comments-v1
   poetry install
   ```

2. **Install ChromeDriver**:
   - Download from: https://chromedriver.chromium.org/
   - Add to PATH or place in project root
   - Or use: `brew install chromedriver` (macOS)

3. **Configure environment**:
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   
   # Create persona (or edit existing)
   cat > data/persona.txt << EOF
   I am a software engineer specializing in AI and automation.
   My communication style is professional yet approachable.
   I focus on practical applications and real-world problem-solving.
   When commenting, I aim to add value through insights or thoughtful questions.
   I avoid generic praise and strive for authenticity.
   EOF
   ```

4. **Test authentication** (Phase I):
   ```bash
   poetry run python -m src.main auth
   ```

5. **Run full pipeline**:
   ```bash
   poetry run python -m src.main full --num-posts 20
   ```

## Usage

### Command Reference

#### Authentication

Authenticate with LinkedIn and save cookies for future use:

```bash
poetry run python -m src.main auth
poetry run python -m src.main auth --headless  # Headless mode
```

**First run**: Opens browser, prompts you to log in, saves cookies.

**Subsequent runs**: Loads cookies, skips login, validates session.

#### Collect Posts

Scrape posts from your LinkedIn feed:

```bash
poetry run python -m src.main collect --num-posts 20
poetry run python -m src.main collect --num-posts 50 --headless
```

**Output**: `data/post_{YYYY-MM-DD-HH-MM-SS}.json`

#### Download Post from URL

Download a single post from a LinkedIn URL:

```bash
poetry run python -m src.main download --url https://www.linkedin.com/feed/update/urn:li:activity:...
poetry run python -m src.main download --url https://www.linkedin.com/feed/update/... --headless
```

**Output**: `data/post_{YYYY-MM-DD-HH-MM-SS}.json`

#### Analyze Posts

Analyze collected posts using LLM to extract summaries and categories:

```bash
poetry run python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json
poetry run python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json --max-workers 5
```

**Options**:
- `--max-workers`: Maximum number of concurrent workers for parallel processing (default: auto)

**Output**: `data/analyzed/post_analyzed_{YYYY-MM-DD-HH-MM-SS}.json`

#### Generate Comments

Generate personalized comment suggestions for analyzed posts:

```bash
poetry run python -m src.main generate --input-file data/analyzed/post_analyzed_2025-11-07-15-00-00.json
poetry run python -m src.main generate --input-file data/analyzed/post_analyzed_2025-11-07-15-00-00.json --max-workers 5
```

**Options**:
- `--max-workers`: Maximum number of concurrent workers for parallel processing (default: auto)

**Output**: `data/posts_processed/post_comments_{post_id}.md` (one file per post)

#### Full Pipeline

Run all phases sequentially:

```bash
poetry run python -m src.main full --num-posts 20
poetry run python -m src.main full --num-posts 20 --headless
```

**Output**:
- `data/post_{date}.json` (collected posts)
- `data/analyzed/post_analyzed_{date}.json` (analyzed posts)
- `data/posts_processed/post_comments_{post_id}.md` (comment suggestions)

### Isolated Testing

Each component can run independently for testing:

```bash
# Services (for development/testing)
poetry run python -m src.services.browser_manager  # Test browser
poetry run python -m src.services.llm_client       # Test LLM

# Features (Phase by Phase)
poetry run python -m src.main auth                 # Phase I: Test auth
poetry run python -m src.main collect --num-posts 10  # Phase II: Collect
poetry run python -m src.main analyze --input-file data/posts-{date}.json  # Phase III
poetry run python -m src.main generate --input-file data/analyzed/posts-analyzed-{date}.json  # Phase IV
```

## Architecture

### Services (Low-level, reusable)

- **`src/services/browser_manager.py`**: Selenium wrapper for browser operations
- **`src/services/llm_client.py`**: Google Gemini LLM integration

### Features (Business logic)

- **`src/features/auth_handler.py`**: LinkedIn authentication and session persistence
- **`src/features/feed_collector.py`**: Feed scraping and post extraction
- **`src/features/post_analyzer.py`**: Post analysis using LLM
- **`src/features/comment_generator.py`**: Comment generation with persona

### Data Flow

```
User → Feed Collector → data/post_{date}.json
                              ↓
                        Post Analyzer (+ LLM, concurrent)
                              ↓
                        data/analyzed/post_analyzed_{date}.json
                              ↓
                        Comment Generator (+ LLM + persona, concurrent)
                              ↓
                        data/posts_processed/post_comments_{post_id}.md
```

### Directory Structure

```
linkedin-comments-v1/
├── src/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   └── browser_manager.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── auth_handler.py
│   │   ├── feed_collector.py
│   │   ├── post_analyzer.py
│   │   └── comment_generator.py
│   └── main.py
├── data/
│   ├── cookies.json              # Session cookies (gitignored)
│   ├── persona.txt                 # Your voice/expertise description
│   ├── prompts/                    # Customizable LLM prompts
│   │   ├── analysis_prompt.txt    # Prompt for post analysis
│   │   └── comment_prompt.txt     # Prompt for comment generation
│   ├── post_{date}.json           # Raw scraped posts (gitignored)
│   ├── analyzed/
│   │   └── post_analyzed_{date}.json  # Posts with LLM analysis (gitignored)
│   ├── posts_processed/
│   │   └── post_comments_{post_id}.md  # Final comment suggestions (gitignored)
│   └── logs/
│       └── run-{date}.log         # Execution logs (gitignored)
├── tests/
├── pyproject.toml
├── Makefile
├── .env                            # API keys (gitignored)
└── README.md
```

## Data Storage

### `data/cookies.json`

Stores LinkedIn session cookies for authentication persistence:

```json
[
  {
    "name": "li_at",
    "value": "...",
    "domain": ".linkedin.com",
    "path": "/",
    "secure": true
  }
]
```

### `data/persona.txt`

Your LinkedIn persona/voice description. Used for comment generation:

```
I am a software engineer specializing in AI and automation.
My communication style is professional yet approachable.
I focus on practical applications and real-world problem-solving.
When commenting, I aim to add value through insights or thoughtful questions.
I avoid generic praise and strive for authenticity.
```

### `data/prompts/analysis_prompt.txt`

Customizable prompt template for post analysis. Uses Python string formatting with `{post_content}` placeholder.

### `data/prompts/comment_prompt.txt`

Customizable prompt template for comment generation. Uses Python string formatting with `{post_content}`, `{summary}`, `{categories}`, and `{persona}` placeholders.

### `data/post_{date}.json`

Raw scraped posts with metadata:

```json
{
  "collected_at": "2025-11-07T14:30:00",
  "num_posts": 20,
  "posts": [
    {
      "post_id": "7128374650293760000",
      "author": "John Doe",
      "author_url": "https://www.linkedin.com/in/johndoe/",
      "content": "Excited to share our new AI product...",
      "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:7128374650293760000/",
      "timestamp": "2h",
      "likes": 42,
      "comments": 5,
      "shares": 2,
      "has_media": true
    }
  ]
}
```

### `data/analyzed/post_analyzed_{date}.json`

Posts enriched with LLM analysis:

```json
{
  "analyzed_at": "2025-11-07T15:00:00",
  "source_file": "posts-2025-11-07-14-30-00.json",
  "posts": [
    {
      "post_id": "7128374650293760000",
      "author": "John Doe",
      "content": "Excited to share our new AI product...",
      "analysis": {
        "summary": "Announcement of a new AI-powered product launch",
        "categories": ["Product Launch", "AI", "Technology"]
      }
    }
  ]
}
```

### `data/posts_processed/post_comments_{post_id}.md`

Comment suggestions in markdown format:

```markdown
# Post Analysis & Comment Suggestions

## Post Details
- **Author**: John Doe
- **URL**: https://www.linkedin.com/feed/update/urn:li:activity:7128374650293760000/
- **Posted**: 2h

## Original Content
Excited to share our new AI product...

## Analysis
**Summary**: Announcement of a new AI-powered product launch
**Categories**: Product Launch, AI, Technology

## Suggested Comments

### Option 1
Congratulations on the launch! The AI-powered features look promising. How are you handling edge cases in the model's predictions?

### Option 2
This looks like a solid solution to a real problem. Have you considered integrating with existing workflow tools to reduce friction for users?

### Option 3
Impressive work! I'm curious about the technical architecture—are you using a specific framework or custom-built solution?

---
*Generated on: 2025-11-07T15:30:00*
```

## Advanced Features

### Concurrent Processing

The system supports parallel processing of posts for both analysis and comment generation, significantly improving performance when processing multiple posts.

- **Analysis**: Posts are analyzed concurrently using `ThreadPoolExecutor`
- **Comment Generation**: Comments are generated concurrently for multiple posts
- **Control**: Use `--max-workers` flag to control the number of concurrent workers

Example:
```bash
# Analyze 20 posts with 5 concurrent workers
poetry run python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json --max-workers 5
```

### Customizable Prompts

LLM prompts are stored in text files and can be customized:

- **Analysis Prompt**: `data/prompts/analysis_prompt.txt`
- **Comment Prompt**: `data/prompts/comment_prompt.txt`

Both prompts use Python string formatting. Edit these files to customize the LLM behavior without changing code.

**Analysis Prompt Placeholders**:
- `{post_content}`: The LinkedIn post content

**Comment Prompt Placeholders**:
- `{post_content}`: The LinkedIn post content
- `{summary}`: The analyzed summary
- `{categories}`: The analyzed categories (comma-separated)
- `{persona}`: Your persona from `data/persona.txt`

### LLM Model Selection

The system supports different LLM models for different tasks:

- **Analysis Model**: Used for post analysis (default: `gemini-2.5-flash`)
- **Comment Model**: Used for comment generation (default: `gemini-2.5-flash`)

Models can be configured by modifying the `LLMClient` initialization in the code, or by setting environment variables (future enhancement).

### URL-Based Post Download

Download individual posts from LinkedIn URLs:

```bash
poetry run python -m src.main download --url https://www.linkedin.com/feed/update/urn:li:activity:...
```

This is useful for:
- Analyzing specific posts
- Testing the system with known posts
- Processing posts shared via links

## Development

### Quick Commands

```bash
make test          # Run tests
make test-cov      # Run tests with coverage report
make lint          # Check code quality
make format        # Format code
make type-check    # Run type checking
make check         # Run all checks
make clean         # Clean up generated files
```

### Code Quality

- **Type Hints**: Required for all function signatures
- **Testing**: Maintain 70% coverage threshold
- **Linting**: Ruff with line length 100
- **Type Checking**: mypy with strict settings
- **Pre-commit**: Hooks run automatically on commit

### Selenium Best Practices

- Use explicit waits: `WebDriverWait(driver, 10).until(...)`
- Handle stale element exceptions with retry logic
- Clean up browser in finally blocks or use context managers
- Use CSS selectors over XPath when possible

### LLM Best Practices

- Validate API responses before parsing
- Implement retry logic with exponential backoff (1s, 2s, 4s)
- Log all prompts and responses for debugging
- Handle rate limits gracefully
- Set reasonable timeouts (30 seconds per request)

## Troubleshooting

### Browser Issues

**ChromeDriver not found**:
```bash
# macOS
brew install chromedriver

# Or download from https://chromedriver.chromium.org/
# Add to PATH
```

**Browser crashes**:
- Check ChromeDriver version matches Chrome version
- Try running without `--headless` flag
- Check system logs for errors

### Authentication Issues

**Cookies not persisting**:
- Ensure `data/` directory exists and is writable
- Check file permissions on `data/cookies.json`
- Try deleting `data/cookies.json` and re-authenticating

**Login validation fails**:
- Ensure you're logged in to LinkedIn in the browser
- Check if LinkedIn UI has changed (selectors may need updating)
- Try manual login again

### LLM API Issues

**API key not found**:
- Ensure `.env` file exists with `GOOGLE_API_KEY=your_key`
- Check file is in project root
- Verify key is valid

**Rate limiting**:
- LLM client includes retry logic with exponential backoff
- If issues persist, reduce number of posts per run
- Check Google Cloud Console for quota limits

**JSON parsing errors**:
- Check logs for raw LLM responses
- LLM may return markdown-wrapped JSON (handled automatically)
- If persistent, adjust prompts in `llm_client.py`

### Feed Scraping Issues

**No posts found**:
- Ensure you're logged in (run `auth` command first)
- Check if LinkedIn feed has loaded (wait longer)
- Verify CSS selectors match current LinkedIn UI

**Stale element exceptions**:
- Retry logic is built-in (3 attempts)
- If persistent, increase wait times
- Check network connection stability

**Duplicates in output**:
- Post ID extraction may fail for some posts
- Check logs for extraction errors
- Verify post ID uniqueness logic

## Future Enhancements

- Headless browser mode as default for automation
- Rate limiting for LLM calls (requests per minute)
- Comment posting automation (requires LinkedIn API or advanced Selenium)
- Analytics dashboard (track engagement over time)
- Multi-persona support (switch between different voices)
- Comment history tracking (avoid duplicate comments on same post)
- Scheduled runs (cron/systemd timers)
- Web UI for reviewing and editing comments before posting
- Export to CSV for analysis
- Integration with CRM or personal knowledge management tools

## License

[Your License Here]

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
