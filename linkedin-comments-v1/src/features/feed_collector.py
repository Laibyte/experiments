"""LinkedIn feed collector for scraping posts."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from src.features.auth_handler import AuthHandler

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)

POST_CONTAINER_SELECTOR = ".feed-shared-update-v2"
# Author selectors (multiple fallbacks)
AUTHOR_NAME_SELECTORS = [
    ".update-components-actor__title",
    ".update-components-actor__meta-link",
    ".update-components-actor__name",
    ".feed-shared-actor__name",
]
AUTHOR_URL_SELECTORS = [
    ".update-components-actor__meta-link",
    ".update-components-actor__link",
    ".feed-shared-actor__link",
]
AUTHOR_DESCRIPTION_SELECTOR = ".update-components-actor__description"
POST_CONTENT_SELECTOR = ".update-components-text"
POST_LINK_SELECTOR = ".feed-shared-update-v2__description a"
TIMESTAMP_SELECTOR = ".update-components-actor__sub-description"
REACTIONS_COUNT_SELECTOR = ".social-details-social-counts__reactions-count"
COMMENTS_COUNT_SELECTOR = ".social-details-social-counts__comments"
SHARES_COUNT_SELECTOR = ".social-details-social-counts__social-actions-text"
# Media selectors
MEDIA_IMAGE_SELECTOR = ".update-components-image img"
MEDIA_VIDEO_SELECTOR = ".feed-shared-video"
MEDIA_DOCUMENT_SELECTOR = ".feed-shared-document"


class FeedCollector:
    """Collects posts from LinkedIn feed."""

    def __init__(self, headless: bool = False) -> None:
        """Initialize feed collector.

        Args:
            headless: Run browser in headless mode.
        """
        self.auth_handler = AuthHandler(headless=headless)
        self.driver: WebDriver | None = None

    def _extract_post_id(self, post_element: "WebElement") -> str | None:
        """Extract post ID from post element.

        Args:
            post_element: Post container element.

        Returns:
            Post ID or None if not found.
        """
        try:
            # Try to get data-urn attribute
            data_urn = post_element.get_attribute("data-urn")
            if data_urn:
                # Extract numeric ID from URN like "urn:li:activity:7128374650293760000"
                match = re.search(r"activity:(\d+)", data_urn)
                if match:
                    return match.group(1)

            # Try to extract from permalink
            try:
                link_elem = post_element.find_element(By.CSS_SELECTOR, POST_LINK_SELECTOR)
                href = link_elem.get_attribute("href")
                if href:
                    match = re.search(r"activity:(\d+)", href)
                    if match:
                        return match.group(1)
            except Exception:
                pass

            # Fallback: use element ID or hash
            element_id = post_element.get_attribute("id")
            if element_id:
                return element_id

            return None
        except Exception as e:
            logger.warning(f"Failed to extract post ID: {e}")
            return None

    def _extract_text_safe(self, element: "WebElement", selector: str) -> str:
        """Safely extract text from element with retry logic.

        Args:
            element: Parent element.
            selector: CSS selector.

        Returns:
            Extracted text or empty string.
        """
        for attempt in range(3):
            try:
                sub_elem = element.find_element(By.CSS_SELECTOR, selector)
                return sub_elem.text.strip()
            except StaleElementReferenceException:
                if attempt < 2:
                    continue
                logger.warning(f"Stale element for {selector} after 3 attempts")
                return ""
            except Exception as e:
                logger.debug(f"Element not found {selector}: {e}")
                return ""
        return ""

    def _extract_text_with_fallbacks(
        self, element: "WebElement", selectors: list[str]
    ) -> str:
        """Extract text using multiple selector fallbacks.

        Args:
            element: Parent element.
            selectors: List of CSS selectors to try.

        Returns:
            Extracted text or empty string.
        """
        for selector in selectors:
            text = self._extract_text_safe(element, selector)
            if text:
                return text
        return ""

    def _extract_count(self, element: "WebElement", selector: str) -> int:
        """Extract numeric count from element.

        Args:
            element: Parent element.
            selector: CSS selector.

        Returns:
            Count as integer, 0 if not found.
        """
        try:
            count_elem = element.find_element(By.CSS_SELECTOR, selector)
            text = count_elem.text.strip()

            # Extract numbers from text like "42 reactions" or "1.2K"
            match = re.search(r"([\d.]+)", text.replace(",", ""))
            if match:
                value = float(match.group(1))
                # Handle K suffix (thousands)
                if "K" in text.upper():
                    return int(value * 1000)
                return int(value)
        except Exception:
            pass
        return 0

    def _extract_url(self, element: "WebElement", selector: str) -> str:
        """Extract URL from element.

        Args:
            element: Parent element.
            selector: CSS selector.

        Returns:
            URL or empty string.
        """
        try:
            link_elem = element.find_element(By.CSS_SELECTOR, selector)
            return link_elem.get_attribute("href") or ""
        except Exception:
            return ""

    def _extract_url_with_fallbacks(
        self, element: "WebElement", selectors: list[str]
    ) -> str:
        """Extract URL using multiple selector fallbacks.

        Args:
            element: Parent element.
            selectors: List of CSS selectors to try.

        Returns:
            URL or empty string.
        """
        for selector in selectors:
            url = self._extract_url(element, selector)
            if url:
                return url
        return ""

    def _clean_author_name(self, author_text: str) -> str:
        """Clean author name by removing extra metadata.

        Args:
            author_text: Raw author text with metadata.

        Returns:
            Cleaned author name.
        """
        if not author_text:
            return ""

        # Split by newlines and take the first line (usually the name)
        lines = author_text.split("\n")
        name = lines[0].strip()

        # Remove common metadata patterns
        # Remove "Verified • Xst/nd/rd/th" patterns
        name = re.sub(r"\s*Verified\s*•\s*\d+[stndrdth]+\s*", "", name, flags=re.IGNORECASE)
        # Remove standalone "Verified" at the end
        name = re.sub(r"\s*Verified\s*$", "", name, flags=re.IGNORECASE)
        # Remove connection degree patterns like "• 1st", "• 2nd", etc.
        name = re.sub(r"\s*•\s*\d+[stndrdth]+\s*", "", name, flags=re.IGNORECASE)
        # Remove extra whitespace
        name = " ".join(name.split())

        return name

    def _extract_media(self, post_element: "WebElement") -> dict:
        """Extract media information from post.

        Args:
            post_element: Post container element.

        Returns:
            Dictionary with media information.
        """
        media_info = {
            "has_media": False,
            "images": [],
            "videos": [],
            "documents": [],
        }

        try:
            # Extract images
            try:
                img_elements = post_element.find_elements(
                    By.CSS_SELECTOR, MEDIA_IMAGE_SELECTOR
                )
                for img in img_elements:
                    src = img.get_attribute("src")
                    alt = img.get_attribute("alt")
                    if src and "profile-displayphoto" not in src:
                        # Filter out profile photos
                        media_info["images"].append({"src": src, "alt": alt or ""})
            except Exception:
                pass

            # Extract videos
            try:
                video_elements = post_element.find_elements(
                    By.CSS_SELECTOR, MEDIA_VIDEO_SELECTOR
                )
                for video in video_elements:
                    src = video.get_attribute("src")
                    poster = video.get_attribute("poster")
                    if src or poster:
                        media_info["videos"].append(
                            {"src": src or "", "poster": poster or ""}
                        )
            except Exception:
                pass

            # Extract documents
            try:
                doc_elements = post_element.find_elements(
                    By.CSS_SELECTOR, MEDIA_DOCUMENT_SELECTOR
                )
                for doc in doc_elements:
                    title = doc.get_attribute("title") or doc.text
                    link = doc.get_attribute("href")
                    if title or link:
                        media_info["documents"].append(
                            {"title": title, "link": link or ""}
                        )
            except Exception:
                pass

            media_info["has_media"] = (
                len(media_info["images"]) > 0
                or len(media_info["videos"]) > 0
                or len(media_info["documents"]) > 0
            )
        except Exception as e:
            logger.debug(f"Error extracting media: {e}")

        return media_info

    def _extract_post_data(self, post_element: "WebElement") -> dict | None:
        """Extract data from a single post element.

        Args:
            post_element: Post container element.

        Returns:
            Post data dictionary or None if extraction fails.
        """
        try:
            post_id = self._extract_post_id(post_element)
            if not post_id:
                logger.warning("Could not extract post ID, skipping post")
                return None

            # Extract author information
            author_raw = self._extract_text_with_fallbacks(post_element, AUTHOR_NAME_SELECTORS)
            # Clean up author name - remove extra metadata like "Verified • 1st"
            author = self._clean_author_name(author_raw)
            author_url = self._extract_url_with_fallbacks(post_element, AUTHOR_URL_SELECTORS)
            author_description = self._extract_text_safe(
                post_element, AUTHOR_DESCRIPTION_SELECTOR
            )

            # Extract content
            content = self._extract_text_safe(post_element, POST_CONTENT_SELECTOR)

            # Try to get post URL from link
            post_url = self._extract_url(post_element, POST_LINK_SELECTOR)
            if not post_url:
                # Fallback: construct URL from post ID
                post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{post_id}/"

            # Extract timestamp
            timestamp = ""
            timestamp_text = self._extract_text_safe(post_element, TIMESTAMP_SELECTOR)
            if timestamp_text:
                # Try to extract datetime attribute from time element
                try:
                    time_elem = post_element.find_element(By.CSS_SELECTOR, "time")
                    timestamp = time_elem.get_attribute("datetime") or timestamp_text
                except Exception:
                    timestamp = timestamp_text
            else:
                # Fallback: try direct time element
                try:
                    time_elem = post_element.find_element(By.CSS_SELECTOR, "time")
                    timestamp = time_elem.get_attribute("datetime") or time_elem.text.strip()
                except Exception:
                    pass

            # Extract engagement metrics
            likes = self._extract_count(post_element, REACTIONS_COUNT_SELECTOR)
            comments = self._extract_count(post_element, COMMENTS_COUNT_SELECTOR)
            shares = self._extract_count(post_element, SHARES_COUNT_SELECTOR)

            # Extract media information
            media_info = self._extract_media(post_element)

            return {
                "post_id": post_id,
                "author": author,
                "author_url": author_url,
                "author_description": author_description,
                "content": content,
                "post_url": post_url,
                "timestamp": timestamp,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "has_media": media_info["has_media"],
                "images": media_info["images"],
                "videos": media_info["videos"],
                "documents": media_info["documents"],
            }
        except StaleElementReferenceException:
            logger.warning("Stale element during post extraction")
            return None
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None

    def _scroll_feed(self) -> None:
        """Scroll feed to load more posts."""
        if not self.driver:
            raise RuntimeError("Browser not started")

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.debug("Scrolled to bottom of page")

    def _wait_for_new_posts(self, current_count: int, timeout: int = 5) -> bool:
        """Wait for new posts to load after scrolling.

        Args:
            current_count: Current number of posts found.
            timeout: Maximum wait time in seconds.

        Returns:
            True if new posts appeared, False otherwise.
        """
        if not self.driver:
            return False

        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                posts = self.driver.find_elements(By.CSS_SELECTOR, POST_CONTAINER_SELECTOR)
                if len(posts) > current_count:
                    logger.debug(f"New posts loaded: {len(posts)} total")
                    return True
            except Exception:
                pass
            time.sleep(0.5)

        return False

    def download_post_from_url(self, post_url: str) -> dict | None:
        """Download a single post from a LinkedIn URL.

        Args:
            post_url: LinkedIn post URL.

        Returns:
            Post data dictionary or None if extraction fails.
        """
        self.driver = self.auth_handler.authenticate()

        if not self.driver:
            raise RuntimeError("Failed to authenticate")

        # Navigate to post URL
        logger.info(f"Downloading post from URL: {post_url}")
        self.auth_handler.browser_manager.navigate_to(post_url)

        # Wait for post to load
        try:
            self.auth_handler.browser_manager.wait_for_element(POST_CONTAINER_SELECTOR, timeout=10)
        except TimeoutException:
            logger.error("Post did not load. Check if URL is valid and you're logged in.")
            return None

        import time

        time.sleep(2)  # Wait for content to fully load

        # Find post element
        try:
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, POST_CONTAINER_SELECTOR)
            if not post_elements:
                logger.error("No post found on page")
                return None

            post_data = self._extract_post_data(post_elements[0])
            if post_data:
                logger.info(f"Successfully downloaded post: {post_data.get('post_id')}")
            return post_data
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None

    def collect_posts(self, num_posts: int = 10) -> list[dict]:
        """Collect posts from LinkedIn feed.

        Args:
            num_posts: Number of posts to collect.

        Returns:
            List of post dictionaries.
        """
        self.driver = self.auth_handler.authenticate()

        if not self.driver:
            raise RuntimeError("Failed to authenticate")

        # Navigate to feed
        self.auth_handler.browser_manager.navigate_to("https://www.linkedin.com/feed/")

        # Wait for feed to load
        try:
            self.auth_handler.browser_manager.wait_for_element(POST_CONTAINER_SELECTOR, timeout=10)
        except TimeoutException:
            logger.error("Feed did not load. Check if you're logged in.")
            raise

        collected_posts: list[dict] = []
        seen_post_ids: set[str] = set()
        scroll_attempts_without_new = 0
        max_scroll_attempts = 3
        max_timeout = 300  # 5 minutes
        start_time = datetime.now()

        logger.info(f"Starting to collect {num_posts} posts...")

        while len(collected_posts) < num_posts:
            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_timeout:
                logger.warning(f"Timeout reached after {elapsed:.0f} seconds")
                break

            # Find all post elements
            try:
                post_elements = self.driver.find_elements(By.CSS_SELECTOR, POST_CONTAINER_SELECTOR)
            except Exception as e:
                logger.error(f"Error finding posts: {e}")
                break

            # Extract data from posts
            for post_elem in post_elements:
                if len(collected_posts) >= num_posts:
                    break

                post_data = self._extract_post_data(post_elem)
                if not post_data:
                    continue

                post_id = post_data["post_id"]
                if post_id in seen_post_ids:
                    continue

                seen_post_ids.add(post_id)
                collected_posts.append(post_data)
                logger.info(f"Collected post {len(collected_posts)}/{num_posts}: {post_data['author']}")

            # Check if we have enough posts
            if len(collected_posts) >= num_posts:
                break

            # Scroll to load more posts
            previous_count = len(post_elements)
            self._scroll_feed()

            # Wait for new posts
            if self._wait_for_new_posts(previous_count, timeout=3):
                scroll_attempts_without_new = 0
            else:
                scroll_attempts_without_new += 1
                if scroll_attempts_without_new >= max_scroll_attempts:
                    logger.warning("No new posts after scrolling, stopping collection")
                    break

        logger.info(f"Collection complete: {len(collected_posts)} posts collected")
        return collected_posts

    def save_posts(self, posts: list[dict], output_file: Path | None = None) -> Path:
        """Save posts to JSON file.

        Args:
            posts: List of post dictionaries.
            output_file: Output file path. If None, generates timestamped filename.

        Returns:
            Path to saved file.
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            output_file = Path(f"data/post_{timestamp}.json")

        output_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "collected_at": datetime.now().isoformat(),
            "num_posts": len(posts),
            "posts": posts,
        }

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(posts)} posts to {output_file}")
        return output_file

    def debug_post_structure(self, num_posts: int = 1) -> Path:
        """Debug method to inspect post structure and dump full data.

        Args:
            num_posts: Number of posts to inspect.
        """
        self.driver = self.auth_handler.authenticate()

        if not self.driver:
            raise RuntimeError("Failed to authenticate")

        # Navigate to feed
        self.auth_handler.browser_manager.navigate_to("https://www.linkedin.com/feed/")

        # Wait for feed to load
        try:
            self.auth_handler.browser_manager.wait_for_element(POST_CONTAINER_SELECTOR, timeout=10)
        except TimeoutException:
            logger.error("Feed did not load. Check if you're logged in.")
            raise

        import time

        time.sleep(3)  # Wait for content to fully load

        # Find post elements
        post_elements = self.driver.find_elements(By.CSS_SELECTOR, POST_CONTAINER_SELECTOR)
        logger.info(f"Found {len(post_elements)} posts on page")

        debug_data = []

        for idx, post_elem in enumerate(post_elements[:num_posts]):
            logger.info(f"Debugging post {idx + 1}/{min(num_posts, len(post_elements))}")

            # Get full HTML
            html_content = post_elem.get_attribute("outerHTML")

            # Get all attributes
            attributes = {}
            try:
                # Get common attributes
                for attr in ["id", "class", "data-urn", "data-activity-id", "data-actor-id"]:
                    val = post_elem.get_attribute(attr)
                    if val:
                        attributes[attr] = val
            except Exception as e:
                logger.warning(f"Error getting attributes: {e}")

            # Try to extract JSON from script tags
            json_data = []
            try:
                script_tags = post_elem.find_elements(By.TAG_NAME, "script")
                for script in script_tags:
                    script_content = script.get_attribute("innerHTML")
                    if script_content and ("{" in script_content or "[" in script_content):
                        json_data.append(script_content[:500])  # First 500 chars
            except Exception:
                pass

            # Try to find all text content
            all_text = ""
            try:
                all_text = post_elem.text
            except Exception:
                pass

            # Try to find all links
            links = []
            try:
                link_elements = post_elem.find_elements(By.TAG_NAME, "a")
                for link in link_elements:
                    href = link.get_attribute("href")
                    text = link.text
                    if href:
                        links.append({"href": href, "text": text})
            except Exception:
                pass

            # Try to find all images
            images = []
            try:
                img_elements = post_elem.find_elements(By.TAG_NAME, "img")
                for img in img_elements:
                    src = img.get_attribute("src")
                    alt = img.get_attribute("alt")
                    if src:
                        images.append({"src": src, "alt": alt})
            except Exception:
                pass

            # Try to find all data attributes
            data_attrs = {}
            try:
                # Get all attributes using JavaScript
                attrs_js = """
                var items = {};
                for (var i = 0; i < arguments[0].attributes.length; i++) {
                    var attr = arguments[0].attributes[i];
                    if (attr.name.startsWith('data-')) {
                        items[attr.name] = attr.value;
                    }
                }
                return items;
                """
                data_attrs = self.driver.execute_script(attrs_js, post_elem)
            except Exception as e:
                logger.warning(f"Error getting data attributes: {e}")

            # Try to find nested elements with common classes
            nested_elements = {}
            common_selectors = {
                "author": [
                    ".update-components-actor__name",
                    ".feed-shared-actor__name",
                    "[data-control-name='actor']",
                    "span[aria-label*='author']",
                ],
                "content": [
                    ".feed-shared-text__text-view",
                    ".feed-shared-text-view",
                    ".update-components-text",
                    "[data-control-name='text']",
                ],
                "timestamp": [
                    "time",
                    ".feed-shared-actor__sub-description",
                    ".update-components-actor__sub-description",
                    "[data-control-name='timestamp']",
                ],
                "reactions": [
                    ".social-details-social-counts__reactions-count",
                    "[data-control-name='reactions_count']",
                ],
                "comments": [
                    ".social-details-social-counts__comments",
                    "[data-control-name='comments_count']",
                ],
            }

            for key, selectors in common_selectors.items():
                for selector in selectors:
                    try:
                        elem = post_elem.find_element(By.CSS_SELECTOR, selector)
                        nested_elements[key] = {
                            "selector": selector,
                            "text": elem.text,
                            "html": elem.get_attribute("outerHTML")[:200],
                        }
                        break
                    except Exception:
                        continue

            debug_data.append(
                {
                    "post_index": idx + 1,
                    "attributes": attributes,
                    "data_attributes": data_attrs,
                    "all_text": all_text[:1000],  # First 1000 chars
                    "links": links[:10],  # First 10 links
                    "images": images[:10],  # First 10 images
                    "nested_elements": nested_elements,
                    "html_snippet": html_content[:2000],  # First 2000 chars
                    "json_snippets": json_data,
                }
            )

        # Save debug data
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        debug_file = Path(f"data/debug-post-structure-{timestamp}.json")
        debug_file.parent.mkdir(parents=True, exist_ok=True)

        with debug_file.open("w", encoding="utf-8") as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Debug data saved to {debug_file}")

        # Also save full HTML of first post
        if post_elements:
            html_file = Path(f"data/debug-post-html-{timestamp}.html")
            with html_file.open("w", encoding="utf-8") as f:
                f.write(post_elements[0].get_attribute("outerHTML"))
            logger.info(f"Full HTML saved to {html_file}")

        return debug_file

    def close(self) -> None:
        """Close browser session."""
        self.auth_handler.close()


if __name__ == "__main__":
    """Test feed collector."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Collect LinkedIn posts")
    parser.add_argument("--num-posts", type=int, default=10, help="Number of posts to collect")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()

    collector = FeedCollector(headless=args.headless)
    try:
        posts = collector.collect_posts(num_posts=args.num_posts)
        output_file = collector.save_posts(posts)
        print(f"\nSuccessfully collected {len(posts)} posts")
        print(f"Saved to: {output_file}")
    finally:
        collector.close()

