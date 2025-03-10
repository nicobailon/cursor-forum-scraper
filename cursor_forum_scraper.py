import os
import json
import re
from time import sleep
from typing import List, Dict, Optional
from urllib.parse import urljoin
import logging
from datetime import datetime
from dateutil.parser import parse
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("crawl_forum.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

if not FIRECRAWL_API_KEY:
    logger.error("FIRECRAWL_API_KEY is not set in your .env file.")
    exit(1)

# Initialize FirecrawlApp instance
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

class ForumCrawler:
    def __init__(self, base_url: str = "https://forum.cursor.com", rate_limit_delay: float = 1.0):
        """Initialize the ForumCrawler with base URL and rate limiting configuration.
        
        Args:
            base_url (str): The base URL of the forum to crawl.
            rate_limit_delay (float): Delay between requests in seconds.
        """
        self.base_url = base_url
        self.latest_posts_url = urljoin(self.base_url, "/latest")
        self.rate_limit_delay = rate_limit_delay

    def extract_post_id(self, url: str) -> Optional[str]:
        """Extract the post ID from a forum post URL.
        
        Args:
            url (str): The URL of the forum post.
            
        Returns:
            Optional[str]: The post ID if found, None otherwise.
        """
        match = re.search(r'/t/[^/]+/(\d+)', url)
        return match.group(1) if match else None

    def parse_post_html(self, html_content: str, post_url: str) -> Dict:
        """Parse HTML content of a forum post to extract structured data.
        
        Args:
            html_content (str): The HTML content of the post page.
            post_url (str): The URL of the post being parsed.
        
        Returns:
            Dict: A dictionary containing post details (title, author, date, etc.).
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title
        title_elem = soup.select_one('h1.topic-title')
        title = title_elem.text.strip() if title_elem else "Unknown"

        # Extract author
        author_elem = soup.select_one('.topic-meta-data .names .username')
        author = author_elem.text.strip() if author_elem else "Unknown"

        # Extract date
        date_elem = soup.select_one('.topic-meta-data .post-date')
        date = "Unknown"
        if date_elem:
            try:
                date_str = date_elem.get('title')
                date = parse(date_str).isoformat() if date_str else "Unknown"
            except Exception as e:
                logger.warning(f"Failed to parse date for post {post_url}: {e}")

        # Extract content
        content_elem = soup.select_one('.topic-body .cooked')
        content = content_elem.text.strip() if content_elem else ""

        # Extract tags
        tags_elems = soup.select('.discourse-tags .discourse-tag')
        tags = [tag.text.strip() for tag in tags_elems] if tags_elems else []

        # Extract replies
        replies_data = []
        replies_elems = soup.select('.topic-post:not(.topic-owner)')
        for reply in replies_elems:
            reply_author_elem = reply.select_one('.names .username')
            reply_author = reply_author_elem.text.strip() if reply_author_elem else "Unknown"

            reply_date_elem = reply.select_one('.post-date')
            reply_date = "Unknown"
            if reply_date_elem:
                try:
                    date_str = reply_date_elem.get('title') or reply_date_elem.text.strip()
                    reply_date = parse(date_str).isoformat() if date_str else "Unknown"
                except Exception as e:
                    logger.warning(f"Failed to parse reply date for post {post_url}: {e}")

            reply_content_elem = reply.select_one('.cooked')
            reply_content = reply_content_elem.text.strip() if reply_content_elem else ""

            replies_data.append({
                "author": reply_author,
                "date": reply_date,
                "content": reply_content
            })

        return {
            "id": self.extract_post_id(post_url),
            "url": post_url,
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "tags": tags,
            "replies": replies_data
        }

    def get_post_links(self) -> List[str]:
        """Retrieve unique links to forum posts from the latest posts page.
        
        Returns:
            List[str]: A list of unique post URLs.
        """
        logger.info(f"Crawling latest posts page: {self.latest_posts_url}")
        params = {
            "crawlerOptions": {
                "limit": 1,
                "includeLinks": True,
                "maxPages": 1
            }
        }

        result = app.crawl_url(self.latest_posts_url, params=params, wait_until_done=True)
        
        post_links_set = set()
        for page in result.get("data", []):
            links_on_page = page.get("links", [])
            for link in links_on_page:
                if "/t/" in link and not link.endswith("/latest") and link.startswith(self.base_url):
                    post_links_set.add(link)
        
        unique_post_links = list(post_links_set)
        logger.info(f"Found {len(unique_post_links)} unique post links")
        return unique_post_links

    def scrape_post(self, url: str) -> Optional[Dict]:
        """Scrape and parse a single forum post.
        
        Args:
            url (str): The URL of the post to scrape.
            
        Returns:
            Optional[Dict]: A dictionary containing the post data if successful, None otherwise.
        """
        logger.info(f"Scraping post URL: {url}")
        
        params = {"formats": ["html", "markdown"], "includeMetadata": True}
        
        try:
            result = app.scrape_url(url=url, params=params)
            
            html_content = result.get("html")
            
            if not html_content:
                logger.error(f"No HTML content found for {url}")
                return None
            
            parsed_data = self.parse_post_html(html_content, url)
            
            # Add markdown content and metadata
            parsed_data["markdown_content"] = result.get("markdown", "")
            parsed_data["metadata"] = result.get("metadata", {})
            
            logger.info(f"Successfully scraped post: {parsed_data['title']} ({url})")
            return parsed_data
        
        except RequestException as e:
            logger.error(f"Request error scraping {url}: {e}")
            return None
        
    def crawl_forum(self, output_file: str):
        """Crawl the forum to extract posts and save the data.
        
        Args:
            output_file (str): Path to the output JSON file.
            
        Returns:
            Dict: The final output data.
        """
        posts_urls = self.get_post_links()
        posts_data_list = []
        
        for idx, post_url in enumerate(posts_urls):
            scraped_data = self.scrape_post(post_url)
            if scraped_data:
                posts_data_list.append(scraped_data)
                logger.info(f"Processed {idx + 1}/{len(posts_urls)} posts")
                sleep(self.rate_limit_delay)
        
        final_output_json = {
            "forum_name": "Cursor Forum",
            "source_url": self.latest_posts_url,
            "crawl_date": datetime.now().isoformat(),
            "posts_count": len(posts_data_list),
            "posts": posts_data_list
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(final_output_json, json_file, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved {len(posts_data_list)} posts to {output_file}")
        except IOError as e:
            logger.error(f"Failed to write to {output_file}: {e}")
            raise
        
        return final_output_json

def main():
    try:
        crawler_instance = ForumCrawler(rate_limit_delay=1.0)
        crawler_instance.crawl_forum("cursor_forum_latest_posts.json")
    except Exception as e:
        logger.error(f"Crawling failed: {e}")
        raise

if __name__ == "__main__":
    main()