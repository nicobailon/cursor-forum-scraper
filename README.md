# Cursor Forum Scraper

This Python script automatically crawls and parses the latest posts from the Cursor Forum (`https://forum.cursor.com/latest`). It systematically extracts detailed content from each individual post, including post metadata, main content, tags, and replies. The scraper leverages the Firecrawl API for efficient crawling and scraping, and BeautifulSoup for precise HTML parsing.

## Features

- **Automated Crawling**: Retrieves the latest posts from the Cursor Forum's latest page (`https://forum.cursor.com/latest`).
- **Detailed Parsing**: Extracts comprehensive details from each individual post thread, including:
  - Post ID
  - URL
  - Title
  - Author
  - Date posted
  - Main content (HTML and Markdown formats)
  - Tags associated with the post
  - Replies (including author, date, and content for each reply)
- **Structured Output**: Saves parsed data in a structured JSON file (`cursor_forum_latest_posts.json`) for easy analysis or further processing.
- **Robust Error Handling**: Logs detailed information about successes and errors during scraping to facilitate debugging.
- **Rate Limiting**: Includes configurable delays between requests to respect server limits.
- **Date Standardization**: Parses dates into ISO 8601 format for consistency.
- **Progress Tracking**: Visual progress bar showing scraping status.
- **Retry Mechanism**: Automatic retries with exponential backoff for failed requests.
- **Command-line Arguments**: Flexible configuration through command-line parameters.

## Example of Parsed Post URL Structure

```
https://forum.cursor.com/t/mcp-add-persistent-memory-in-cursor/57497
```

## Requirements

Before running the script, ensure you have:

- Python installed (version 3.8 or higher recommended).
- A valid API key from [Firecrawl](https://firecrawl.dev/).
- `uv` installed (recommended) or pip for dependency management.

## Installation

### Using uv (Recommended)

1. Install `uv` if you haven't already:
```bash
pip install uv
```

2. Clone this repository:
```bash
git clone https://github.com/nicobailon/cursor-forum-scraper.git
cd cursor-forum-scraper
```

3. Create a `.env` file in your project's root directory containing your Firecrawl API key:
```
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

The dependencies listed in `requirements.txt` will be automatically installed when running the script with `uv run`.

### Using pip

1. Install required dependencies using pip:
```bash
pip install firecrawl beautifulsoup4 python-dotenv python-dateutil tqdm
```

2. Create a `.env` file in your project's root directory containing your Firecrawl API key:
```
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

## Usage

### Using uv run (Recommended)

Run the script directly with uv run:

```bash
uv run python cursor_forum_scraper.py
```

This will automatically create a virtual environment, install all dependencies from requirements.txt, and run the script.

### Command-line Arguments

The script supports several command-line arguments for customization:

```bash
uv run python cursor_forum_scraper.py --help
```

```
usage: cursor_forum_scraper.py [-h] [--base-url BASE_URL] [--output-file OUTPUT_FILE]
                             [--rate-limit-delay RATE_LIMIT_DELAY] [--max-posts MAX_POSTS]

Crawl Cursor Forum posts

optional arguments:
  -h, --help            show this help message and exit
  --base-url BASE_URL   Base URL of the forum
  --output-file OUTPUT_FILE
                        Output JSON file
  --rate-limit-delay RATE_LIMIT_DELAY
                        Minimum delay between requests in seconds
  --max-posts MAX_POSTS
                        Maximum number of posts to scrape
```

### Examples

Default run (with uv):
```bash
uv run python cursor_forum_scraper.py
```

Customize output file and rate limit:
```bash
uv run python cursor_forum_scraper.py --output-file "my_posts.json" --rate-limit-delay 2.0
```

Limit to 5 posts for testing:
```bash
uv run python cursor_forum_scraper.py --max-posts 5
```

## Output Structure

The resulting JSON file (`cursor_forum_latest_posts.json` by default) will have this structure:

```json
{
  "forum_name": "Cursor Forum",
  "source_url": "https://forum.cursor.com/latest",
  "crawl_date": "2025-03-09T13:37:00",
  "posts_count": 10,
  "posts": [
    {
      "id": "57497",
      "url": "https://forum.cursor.com/t/mcp-add-persistent-memory-in-cursor/57497",
      "title": "MCP: Add Persistent Memory in Cursor",
      "author": "username",
      "date": "2025-03-08T10:15:00",
      "content": "Post content here...",
      "tags": ["tag1", "tag2"],
      "replies": [
        {
          "author": "reply_author",
          "date": "2025-03-08T11:00:00",
          "content": "Reply content here..."
        }
      ],
      "markdown_content": "# Markdown formatted content...",
      "metadata": {
        "...": "..."
      }
    },
    ...
  ]
}
```

## Logging

The script generates a log file named `crawl_forum.log`, recording detailed information about each step of the scraping process, including:
- Crawling status and found post links
- Individual post scraping progress and titles
- Errors and warnings encountered during execution

## HTML Structure Assumptions

The script assumes the following HTML structure for Cursor Forum posts:

- Post titles: `h1.topic-title`
- Post authors: `.topic-meta-data .names .username`
- Post dates: `.topic-meta-data .post-date` (title attribute)
- Post content: `.topic-body .cooked`
- Tags: `.discourse-tags .discourse-tag`
- Replies: `.topic-post:not(.topic-owner)` with nested elements for author, date, and content

If the forum structure changes, these selectors may need to be updated.

## Advanced Features

### Retry Mechanism

The script automatically retries failed requests up to 3 times with exponential backoff (1s, 2s, 4s) to handle transient network issues.

### Adaptive Rate Limiting

Rather than using a fixed delay between requests, the script measures the time taken for each scrape operation and only waits for the remaining time needed to meet the minimum delay. This optimizes throughput while still respecting rate limits.

### Progress Visualization

A progress bar displays real-time status of the scraping operation, showing completed/total posts and estimated time remaining.

## Benefits of Using uv

- **Dependency Management**: Automatically installs all required packages from requirements.txt
- **Isolated Environment**: Creates or uses a virtual environment for the script
- **Reproducibility**: Ensures consistent execution across different systems
- **Speed**: uv is significantly faster than traditional pip for dependency installation

## Error Handling

The script includes robust error handling for:
- API key validation
- Request errors during scraping (with retries)
- HTML parsing issues
- Date parsing failures
- File writing operations

This makes the script resilient to common issues that may occur during web scraping.

## Future Enhancements

Potential improvements for future versions:
- Incremental scraping: Only scrape posts newer than previous runs
- Filters: Add options to filter posts by tag, author, or date range
- Analytics: Built-in basic analysis of scraped data

This script is designed to be robust, maintainable, scalable, and respectful of server resources.