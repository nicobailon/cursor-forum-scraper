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

## Example of Parsed Post URL Structure

```
https://forum.cursor.com/t/mcp-add-persistent-memory-in-cursor/57497
```

## Requirements

Before running the script, ensure you have:

- Python installed (version 3.8 or higher recommended).
- A valid API key from [Firecrawl](https://firecrawl.dev/).

## Installation

1. Install required dependencies using pip:

```bash
pip install firecrawl beautifulsoup4 python-dotenv requests python-dateutil
```

2. Create a `.env` file in your project's root directory containing your Firecrawl API key:

```
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

## Usage

Run the script directly from the command line:

```bash
python cursor_forum_scraper.py
```

Upon completion, the script will generate:

- A JSON file (`cursor_forum_latest_posts.json`) containing structured data of all scraped posts.
- A log file (`crawl_forum.log`) detailing the scraping process and any encountered issues.

## Output Structure

The resulting JSON file (`cursor_forum_latest_posts.json`) will have this structure:

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

## Customization Options

You can adjust settings in the script such as:

- `rate_limit_delay`: Modify delay between requests to avoid overwhelming servers.
- `output_file`: Change name or location of output JSON file.
- Base URL: Change the target forum by modifying the `base_url` parameter when initializing `ForumCrawler`.

## Error Handling

The script includes robust error handling for:
- API key validation
- Request errors during scraping
- HTML parsing issues
- Date parsing failures
- File writing operations

This makes the script resilient to common issues that may occur during web scraping.

## Future Enhancements

Potential improvements for future versions:
- Configurability: Add command-line parameters for the number of posts to scrape or custom rate limits.
- Resume Capability: Save intermediate results to resume scraping after failures.
- Validation: Add more comprehensive data validation.

This script is designed to be robust, maintainable, scalable, and respectful of server resources.