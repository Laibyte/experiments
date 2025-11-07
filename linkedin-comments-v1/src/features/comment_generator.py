"""Comment generator using LLM to create personalized comment suggestions."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from src.services.llm_client import LLMClient

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

PERSONA_FILE = Path("src/lib/persona.txt")


class CommentGenerator:
    """Generates personalized comment suggestions for posts."""

    def __init__(self, max_workers: int | None = None) -> None:
        """Initialize comment generator.

        Args:
            max_workers: Maximum number of concurrent workers. If None, uses default.
        """
        self.llm_client = LLMClient()
        self.persona = self._load_persona()
        self.max_workers = max_workers

    def _load_persona(self) -> str:
        """Load persona from file.

        Returns:
            Persona text.

        Raises:
            FileNotFoundError: If persona file doesn't exist.
            ValueError: If persona file is empty.
        """
        if not PERSONA_FILE.exists():
            raise FileNotFoundError(f"Persona file not found: {PERSONA_FILE}")

        with PERSONA_FILE.open(encoding="utf-8") as f:
            persona = f.read().strip()

        if not persona:
            raise ValueError(f"Persona file is empty: {PERSONA_FILE}")

        logger.info(f"Loaded persona from {PERSONA_FILE}")
        return persona

    def load_analyzed_posts(self, input_file: Path) -> dict:
        """Load analyzed posts from JSON file.

        Args:
            input_file: Path to input JSON file.

        Returns:
            Dictionary with analyzed posts data.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file is not valid JSON.
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        with input_file.open(encoding="utf-8") as f:
            data = json.load(f)

        posts = data.get("posts", [])
        logger.info(f"Loaded {len(posts)} analyzed posts from {input_file}")
        return data

    def generate_comment_markdown(self, post: dict, comments: list[str]) -> str:
        """Generate markdown content for a post with comments.

        Args:
            post: Post dictionary with all data.
            comments: List of comment suggestions.

        Returns:
            Markdown content string.
        """
        author = post.get("author", "Unknown")
        post_url = post.get("post_url", "")
        timestamp = post.get("timestamp", "")
        content = post.get("content", "")
        analysis = post.get("analysis", {})
        summary = analysis.get("summary", "")
        categories = analysis.get("categories", [])
        generated_at = datetime.now().isoformat()

        categories_str = ", ".join(categories) if categories else "None"

        # Escape markdown special characters in content
        content_escaped = content.replace("```", "\\`\\`\\`")

        markdown = f"""# Post Analysis & Comment Suggestions

## Post Details

- **Author**: {author}
- **URL**: {post_url}
- **Posted**: {timestamp}

## Original Content

{content_escaped}

## Analysis

**Summary**: {summary}

**Categories**: {categories_str}

## Suggested Comments

### Option 1

{comments[0] if len(comments) > 0 else "Error: No comment generated"}

### Option 2

{comments[1] if len(comments) > 1 else "Error: No comment generated"}

### Option 3

{comments[2] if len(comments) > 2 else "Error: No comment generated"}

---

*Generated on: {generated_at}*
"""

        return markdown

    def generate_comments_for_post(self, post: dict) -> list[str]:
        """Generate comment suggestions for a single post.

        Args:
            post: Post dictionary with content and analysis.

        Returns:
            List of comment suggestions (3 comments).
        """
        content = post.get("content", "")
        analysis = post.get("analysis", {})
        summary = analysis.get("summary", "")
        categories = analysis.get("categories", [])

        if not content:
            logger.warning(f"Post {post.get('post_id')} has no content, skipping")
            return ["Error: No content", "Error: No content", "Error: No content"]

        try:
            comments = self.llm_client.generate_comments(
                post_content=content,
                summary=summary,
                categories=categories,
                persona=self.persona,
            )
            return comments
        except Exception as e:
            logger.error(f"Error generating comments for post {post.get('post_id')}: {e}")
            return [f"Error: {str(e)}", f"Error: {str(e)}", f"Error: {str(e)}"]

    def _process_single_post(self, post: dict) -> dict:
        """Process a single post and generate comments.

        Args:
            post: Post dictionary.

        Returns:
            Post dictionary with generated comments.
        """
        post_id = post.get("post_id", "unknown")
        logger.info(f"Generating comments for post: {post_id}")

        try:
            comments = self.generate_comments_for_post(post)
            post["generated_comments"] = comments
            logger.info(f"  Generated {len(comments)} comments")
        except Exception as e:
            logger.error(f"Error processing post {post_id}: {e}")
            post["generated_comments"] = [
                f"Error: {str(e)}",
                f"Error: {str(e)}",
                f"Error: {str(e)}",
            ]

        return post

    def process_posts(self, analyzed_posts_data: dict, concurrent: bool = True) -> list[dict]:
        """Process all analyzed posts and generate comments.

        Args:
            analyzed_posts_data: Dictionary with analyzed posts.
            concurrent: Whether to process posts concurrently.

        Returns:
            List of post dictionaries with generated comments.
        """
        posts = analyzed_posts_data.get("posts", [])
        processed_posts: list[dict] = []

        logger.info(f"Generating comments for {len(posts)} posts (concurrent={concurrent})...")

        if concurrent and len(posts) > 1:
            # Process posts concurrently
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_post = {
                    executor.submit(self._process_single_post, post): post
                    for post in posts
                }

                for i, future in enumerate(as_completed(future_to_post), 1):
                    try:
                        processed_post = future.result()
                        processed_posts.append(processed_post)
                        logger.info(f"Completed {i}/{len(posts)} posts")
                    except Exception as e:
                        original_post = future_to_post[future]
                        post_id = original_post.get("post_id", "unknown")
                        logger.error(f"Error processing post {post_id}: {e}")
                        original_post["generated_comments"] = [
                            f"Error: {str(e)}",
                            f"Error: {str(e)}",
                            f"Error: {str(e)}",
                        ]
                        processed_posts.append(original_post)
        else:
            # Process posts sequentially
            for i, post in enumerate(posts, 1):
                post_id = post.get("post_id", "unknown")
                logger.info(f"Generating comments for post {i}/{len(posts)}: {post_id}")
                processed_post = self._process_single_post(post)
                processed_posts.append(processed_post)

        # Sort by original order
        post_id_to_index = {post.get("post_id"): i for i, post in enumerate(posts)}
        processed_posts.sort(
            key=lambda p: post_id_to_index.get(p.get("post_id"), float("inf"))
        )

        return processed_posts

    def save_comment_files(self, processed_posts: list[dict]) -> list[Path]:
        """Save comment markdown files for each post.

        Args:
            processed_posts: List of processed post dictionaries.

        Returns:
            List of saved file paths.
        """
        output_dir = Path("data/posts_processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []

        for post in processed_posts:
            post_id = post.get("post_id", "unknown")
            comments = post.get("generated_comments", [])

            markdown = self.generate_comment_markdown(post, comments)

            output_file = output_dir / f"post_comments_{post_id}.md"
            with output_file.open("w", encoding="utf-8") as f:
                f.write(markdown)

            saved_files.append(output_file)
            logger.info(f"Saved comment file: {output_file}")

        return saved_files

    def run(self, input_file: Path) -> list[Path]:
        """Run full comment generation pipeline.

        Args:
            input_file: Path to input JSON file with analyzed posts.

        Returns:
            List of saved markdown file paths.
        """
        # Load analyzed posts
        analyzed_posts_data = self.load_analyzed_posts(input_file)

        # Generate comments
        processed_posts = self.process_posts(analyzed_posts_data, concurrent=True)

        # Save markdown files
        saved_files = self.save_comment_files(processed_posts)

        # Print summary
        successful = sum(
            1
            for p in processed_posts
            if not any("Error" in c for c in p.get("generated_comments", []))
        )
        failed = len(processed_posts) - successful

        print("\n" + "=" * 60)
        print("Comment Generation Complete")
        print("=" * 60)
        print(f"Total posts: {len(processed_posts)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print("Output directory: data/posts_processed/")
        print(f"Files generated: {len(saved_files)}")
        print("=" * 60)

        return saved_files


if __name__ == "__main__":
    """Test comment generator."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Generate comment suggestions for LinkedIn posts")
    parser.add_argument(
        "--input-file",
        type=Path,
        required=True,
        help="Input JSON file with analyzed posts",
    )
    args = parser.parse_args()

    generator = CommentGenerator()
    generator.run(args.input_file)

