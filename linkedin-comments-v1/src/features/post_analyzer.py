"""Post analyzer using LLM to extract summaries and categories."""

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


class PostAnalyzer:
    """Analyzes posts using LLM to extract summaries and categories."""

    def __init__(self, max_workers: int | None = None) -> None:
        """Initialize post analyzer.

        Args:
            max_workers: Maximum number of concurrent workers. If None, uses default.
        """
        self.llm_client = LLMClient()
        self.max_workers = max_workers

    def load_posts(self, input_file: Path) -> dict:
        """Load posts from JSON file.

        Args:
            input_file: Path to input JSON file.

        Returns:
            Dictionary with posts data.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file is not valid JSON.
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        with input_file.open(encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Loaded {len(data.get('posts', []))} posts from {input_file}")
        return data

    def _analyze_single_post(self, post: dict) -> dict:
        """Analyze a single post.

        Args:
            post: Post dictionary.

        Returns:
            Analyzed post dictionary.
        """
        post_id = post.get("post_id", "unknown")
        content = post.get("content", "")

        if not content:
            logger.warning(f"Post {post_id} has no content, skipping analysis")
            post["analysis"] = {"summary": "No content", "categories": []}
            return post

        logger.info(f"Analyzing post: {post_id}")

        try:
            analysis = self.llm_client.analyze_post(content)
            post["analysis"] = analysis
            logger.info(f"  Summary: {analysis['summary'][:60]}...")
            logger.info(f"  Categories: {', '.join(analysis['categories'])}")
        except Exception as e:
            logger.error(f"Error analyzing post {post_id}: {e}")
            post["analysis"] = {"summary": f"Error: {str(e)}", "categories": []}

        return post

    def analyze_posts(self, posts_data: dict, concurrent: bool = True) -> list[dict]:
        """Analyze all posts using LLM.

        Args:
            posts_data: Dictionary with posts data.
            concurrent: Whether to process posts concurrently.

        Returns:
            List of analyzed post dictionaries.
        """
        posts = posts_data.get("posts", [])
        analyzed_posts: list[dict] = []

        logger.info(f"Analyzing {len(posts)} posts (concurrent={concurrent})...")

        if concurrent and len(posts) > 1:
            # Process posts concurrently
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_post = {
                    executor.submit(self._analyze_single_post, post): post
                    for post in posts
                }

                for i, future in enumerate(as_completed(future_to_post), 1):
                    try:
                        analyzed_post = future.result()
                        analyzed_posts.append(analyzed_post)
                        logger.info(f"Completed {i}/{len(posts)} posts")
                    except Exception as e:
                        original_post = future_to_post[future]
                        post_id = original_post.get("post_id", "unknown")
                        logger.error(f"Error processing post {post_id}: {e}")
                        original_post["analysis"] = {
                            "summary": f"Error: {str(e)}",
                            "categories": [],
                        }
                        analyzed_posts.append(original_post)
        else:
            # Process posts sequentially
            for i, post in enumerate(posts, 1):
                post_id = post.get("post_id", "unknown")
                logger.info(f"Analyzing post {i}/{len(posts)}: {post_id}")
                analyzed_post = self._analyze_single_post(post)
                analyzed_posts.append(analyzed_post)

        # Sort by original order
        post_id_to_index = {post.get("post_id"): i for i, post in enumerate(posts)}
        analyzed_posts.sort(
            key=lambda p: post_id_to_index.get(p.get("post_id"), float("inf"))
        )

        return analyzed_posts

    def save_analyzed_posts(
        self,
        analyzed_posts: list[dict],
        source_file: Path,
        output_file: Path | None = None,
    ) -> Path:
        """Save analyzed posts to JSON file.

        Args:
            analyzed_posts: List of analyzed post dictionaries.
            source_file: Source file path for reference.
            output_file: Output file path. If None, generates timestamped filename.

        Returns:
            Path to saved file.
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            output_file = Path(f"data/analyzed/post_analyzed_{timestamp}.json")

        output_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "analyzed_at": datetime.now().isoformat(),
            "source_file": str(source_file),
            "posts": analyzed_posts,
        }

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(analyzed_posts)} analyzed posts to {output_file}")
        return output_file

    def run(self, input_file: Path, output_file: Path | None = None) -> Path:
        """Run full analysis pipeline.

        Args:
            input_file: Path to input JSON file.
            output_file: Output file path. If None, generates timestamped filename.

        Returns:
            Path to saved file.
        """
        # Load posts
        posts_data = self.load_posts(input_file)

        # Analyze posts
        analyzed_posts = self.analyze_posts(posts_data, concurrent=True)

        # Save results
        output_path = self.save_analyzed_posts(analyzed_posts, input_file, output_file)

        # Print summary
        successful = sum(1 for p in analyzed_posts if "Error" not in p.get("analysis", {}).get("summary", ""))
        failed = len(analyzed_posts) - successful

        print("\n" + "=" * 60)
        print("Analysis Complete")
        print("=" * 60)
        print(f"Total posts: {len(analyzed_posts)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Output file: {output_path}")
        print("=" * 60)

        return output_path


if __name__ == "__main__":
    """Test post analyzer."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"data/logs/analyzer-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"),
            logging.StreamHandler(),
        ],
    )

    parser = argparse.ArgumentParser(description="Analyze LinkedIn posts using LLM")
    parser.add_argument("--input-file", type=Path, required=True, help="Input JSON file with posts")
    args = parser.parse_args()

    analyzer = PostAnalyzer()
    analyzer.run(args.input_file)

