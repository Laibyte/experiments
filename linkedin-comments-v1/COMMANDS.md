# LinkedIn Comment Automation - Command Reference

Complete list of all available CLI commands with their flags and descriptions.

## Global Flags

These flags are available for all commands:

- `--headless`: Run browser in headless mode (no visible browser window)

---

## Commands

### 1. `auth`
**Purpose**: Authenticate with LinkedIn and save session cookies for future use.

**Description**: Opens a browser window, prompts you to log in to LinkedIn, and saves authentication cookies. On subsequent runs, it loads the saved cookies and validates the session without requiring login.

**Flags**:
- `--headless` (optional): Run browser in headless mode

**Example**:
```bash
poetry run python -m src.main auth
poetry run python -m src.main auth --headless
```

**Output**: Saves cookies to `data/cookies.json`

---

### 2. `collect`
**Purpose**: Scrape posts from your LinkedIn feed.

**Description**: Navigates to your LinkedIn feed, scrolls to load posts, and extracts post data (author, content, engagement metrics, etc.) from the feed.

**Flags**:
- `--num-posts` (required): Number of posts to collect (default: 10)
- `--headless` (optional): Run browser in headless mode

**Example**:
```bash
poetry run python -m src.main collect --num-posts 20
poetry run python -m src.main collect --num-posts 50 --headless
```

**Output**: `data/post_{YYYY-MM-DD-HH-MM-SS}.json`

---

### 3. `download`
**Purpose**: Download a single post from a specific LinkedIn URL.

**Description**: Navigates to a LinkedIn post URL and extracts the post data. Useful for analyzing specific posts shared via links.

**Flags**:
- `--url` (required): LinkedIn post URL
- `--headless` (optional): Run browser in headless mode

**Example**:
```bash
poetry run python -m src.main download --url https://www.linkedin.com/feed/update/urn:li:activity:7128374650293760000/
poetry run python -m src.main download --url https://www.linkedin.com/feed/update/... --headless
```

**Output**: `data/post_{YYYY-MM-DD-HH-MM-SS}.json`

---

### 4. `analyze`
**Purpose**: Analyze collected posts using LLM to extract summaries and categories.

**Description**: Takes a JSON file with collected posts and uses an LLM to analyze each post, extracting a summary and relevant categories. Supports concurrent processing for faster analysis of multiple posts.

**Flags**:
- `--input-file` (required): Path to JSON file with collected posts
- `--max-workers` (optional): Maximum number of concurrent workers for parallel processing (default: auto)
- `--headless` (optional): Not applicable (no browser needed)

**Example**:
```bash
poetry run python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json
poetry run python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json --max-workers 5
```

**Output**: `data/analyzed/post_analyzed_{YYYY-MM-DD-HH-MM-SS}.json`

**Note**: Posts with no content are automatically skipped (marked as "No content" in analysis).

---

### 5. `generate`
**Purpose**: Generate personalized comment suggestions for analyzed posts.

**Description**: Takes a JSON file with analyzed posts and uses an LLM to generate 3 distinct comment suggestions for each post, based on your persona. Supports concurrent processing for faster generation of multiple comments.

**Flags**:
- `--input-file` (required): Path to JSON file with analyzed posts
- `--max-workers` (optional): Maximum number of concurrent workers for parallel processing (default: auto)
- `--headless` (optional): Not applicable (no browser needed)

**Example**:
```bash
poetry run python -m src.main generate --input-file data/analyzed/post_analyzed_2025-11-07-15-00-00.json
poetry run python -m src.main generate --input-file data/analyzed/post_analyzed_2025-11-07-15-00-00.json --max-workers 5
```

**Output**: `data/posts_processed/post_comments_{post_id}.md` (one file per post)

**Note**: Posts with no content are automatically skipped.

---

### 6. `full`
**Purpose**: Run the complete pipeline: collect → analyze → generate comments.

**Description**: Executes all phases sequentially: (1) Authenticate, (2) Collect posts from feed, (3) Analyze posts with LLM, (4) Generate comment suggestions. This is the most convenient command for end-to-end processing.

**Flags**:
- `--num-posts` (optional): Number of posts to collect (default: 10)
- `--max-workers` (optional): Maximum number of concurrent workers for analysis and generation phases (default: auto)
- `--headless` (optional): Run browser in headless mode

**Example**:
```bash
poetry run python -m src.main full --num-posts 20
poetry run python -m src.main full --num-posts 20 --max-workers 5
poetry run python -m src.main full --num-posts 20 --max-workers 5 --headless
```

**Output**:
- `data/post_{date}.json` (collected posts)
- `data/analyzed/post_analyzed_{date}.json` (analyzed posts)
- `data/posts_processed/post_comments_{post_id}.md` (comment suggestions)

**Note**: The `--max-workers` flag applies to both the analysis and comment generation phases.

---

### 7. `debug`
**Purpose**: Debug and inspect LinkedIn post structure (DOM/JSON).

**Description**: Collects detailed debugging information about post structure, including HTML, attributes, selectors, and extracted data. Useful for troubleshooting when post extraction fails or LinkedIn UI changes.

**Flags**:
- `--num-posts` (optional): Number of posts to debug (default: 1)
- `--headless` (optional): Run browser in headless mode

**Example**:
```bash
poetry run python -m src.main debug --num-posts 3
poetry run python -m src.main debug --num-posts 1 --headless
```

**Output**:
- `data/debug-post-structure-{timestamp}.json` (structured debug data)
- `data/debug-post-html-{timestamp}.html` (raw HTML of first post)

---

## Command Workflow Examples

### Basic Workflow (Step by Step)
```bash
# 1. Authenticate (first time only)
poetry run python -m src.main auth

# 2. Collect posts
poetry run python -m src.main collect --num-posts 20

# 3. Analyze posts
poetry run python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json

# 4. Generate comments
poetry run python -m src.main generate --input-file data/analyzed/post_analyzed_2025-11-07-15-00-00.json
```

### Quick Workflow (Full Pipeline)
```bash
# Run everything in one command
poetry run python -m src.main full --num-posts 20 --max-workers 5
```

### Download and Process Single Post
```bash
# 1. Download post from URL
poetry run python -m src.main download --url https://www.linkedin.com/feed/update/...

# 2. Analyze the downloaded post
poetry run python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json

# 3. Generate comments
poetry run python -m src.main generate --input-file data/analyzed/post_analyzed_2025-11-07-15-00-00.json
```

---

## Performance Tips

- **Concurrent Processing**: Use `--max-workers` flag for `analyze` and `generate` commands when processing multiple posts (recommended: 3-5 workers)
- **Headless Mode**: Use `--headless` flag for faster execution when you don't need to see the browser
- **Batch Processing**: For large batches, consider processing in smaller chunks to avoid rate limits

---

## Notes

- All commands support the `--headless` flag (except `analyze` and `generate` which don't use a browser)
- The `--max-workers` flag is available for `analyze`, `generate`, and `full` commands
- Posts with no content are automatically skipped during analysis
- File naming follows the pattern: `post_{date}.json`, `post_analyzed_{date}.json`, `post_comments_{post_id}.md`
- All output files are saved in the `data/` directory structure

