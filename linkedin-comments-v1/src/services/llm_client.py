"""LLM client service for Google Gemini integration."""

import json
import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

import google.generativeai as genai
from dotenv import load_dotenv

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

load_dotenv()

DEFAULT_ANALYSIS_MODEL = "gemini-2.5-flash"
DEFAULT_COMMENT_MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
INITIAL_BACKOFF = 1

ANALYSIS_PROMPT_FILE = Path("src/lib/analysis_prompt.txt")
COMMENT_PROMPT_FILE = Path("src/lib/comment_prompt.txt")


class LLMClient:
    """Client for Google Gemini LLM."""

    def __init__(
        self,
        analysis_model: str | None = None,
        comment_model: str | None = None,
        analysis_prompt_file: Path | None = None,
        comment_prompt_file: Path | None = None,
    ) -> None:
        """Initialize LLM client.

        Args:
            analysis_model: Model name for analysis tasks. Defaults to DEFAULT_ANALYSIS_MODEL.
            comment_model: Model name for comment generation. Defaults to DEFAULT_COMMENT_MODEL.
            analysis_prompt_file: Path to analysis prompt file. Defaults to ANALYSIS_PROMPT_FILE.
            comment_prompt_file: Path to comment prompt file. Defaults to COMMENT_PROMPT_FILE.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)

        self.analysis_model_name = analysis_model or DEFAULT_ANALYSIS_MODEL
        self.comment_model_name = comment_model or DEFAULT_COMMENT_MODEL
        self.analysis_model = genai.GenerativeModel(self.analysis_model_name)
        self.comment_model = genai.GenerativeModel(self.comment_model_name)

        self.analysis_prompt_file = analysis_prompt_file or ANALYSIS_PROMPT_FILE
        self.comment_prompt_file = comment_prompt_file or COMMENT_PROMPT_FILE

        logger.info(
            f"Initialized LLM client - Analysis: {self.analysis_model_name}, "
            f"Comments: {self.comment_model_name}"
        )

    def _load_prompt_template(self, prompt_file: Path) -> str:
        """Load prompt template from file.

        Args:
            prompt_file: Path to prompt template file.

        Returns:
            Prompt template string.

        Raises:
            FileNotFoundError: If prompt file doesn't exist.
        """
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        with prompt_file.open(encoding="utf-8") as f:
            return f.read().strip()

    def _call_with_retry(self, prompt: str, model: genai.GenerativeModel) -> str:
        """Call LLM with retry logic and exponential backoff.

        Args:
            prompt: Prompt text.
            model: Generative model to use.

        Returns:
            Response text.

        Raises:
            Exception: If all retries fail.
        """
        last_exception = None
        backoff = INITIAL_BACKOFF

        for attempt in range(MAX_RETRIES):
            try:
                response = model.generate_content(prompt)
                if not response.text:
                    raise ValueError("Empty response from LLM")
                return response.text
            except Exception as e:
                last_exception = e
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.error("All retries failed for LLM call")
                    raise

        raise last_exception or Exception("Unknown error in LLM call")

    def analyze_post(self, post_content: str) -> dict[str, str | list[str]]:
        """Analyze a LinkedIn post and extract summary and categories.

        Args:
            post_content: Post content text.

        Returns:
            Dictionary with 'summary' and 'categories' keys.
        """
        try:
            prompt_template = self._load_prompt_template(self.analysis_prompt_file)
            prompt = prompt_template.format(post_content=post_content)
        except FileNotFoundError:
            # Fallback to default prompt if file not found
            logger.warning(f"Prompt file not found: {self.analysis_prompt_file}, using default")
            prompt = f"""Analyze this LinkedIn post. Provide a one-sentence summary and 2-4 relevant categories (e.g., AI, Career Advice, Product Launch, Technology, Business).

Post content:
{post_content}

Return JSON format:
{{
  "summary": "One-sentence summary of the post",
  "categories": ["Category1", "Category2", "Category3"]
}}

Only return the JSON, no additional text."""

        try:
            response_text = self._call_with_retry(prompt, self.analysis_model)
            # Try to extract JSON from response
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text

            # Parse JSON
            analysis = json.loads(response_text)

            # Validate structure
            if "summary" not in analysis or "categories" not in analysis:
                raise ValueError("Invalid response structure")

            if not isinstance(analysis["summary"], str):
                raise ValueError("Summary must be a string")

            if not isinstance(analysis["categories"], list):
                raise ValueError("Categories must be a list")

            logger.debug(f"Post analyzed: {analysis['summary'][:50]}...")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text}")
            return {"summary": "Error: Failed to parse analysis", "categories": []}
        except Exception as e:
            logger.error(f"Error analyzing post: {e}")
            return {"summary": f"Error: {str(e)}", "categories": []}

    def generate_comments(
        self,
        post_content: str,
        summary: str,
        categories: list[str],
        persona: str,
    ) -> list[str]:
        """Generate comment suggestions for a post.

        Args:
            post_content: Original post content.
            summary: Post summary.
            categories: Post categories.
            persona: User persona text.

        Returns:
            List of comment suggestions (3 comments).
        """
        categories_str = ", ".join(categories)
        try:
            prompt_template = self._load_prompt_template(self.comment_prompt_file)
            prompt = prompt_template.format(
                post_content=post_content,
                summary=summary,
                categories=categories_str,
                persona=persona,
            )
        except FileNotFoundError:
            # Fallback to default prompt if file not found
            logger.warning(f"Prompt file not found: {self.comment_prompt_file}, using default")
            prompt = f"""Given this LinkedIn post, summary, categories, and my persona, generate 3 distinct comment suggestions. Make them authentic, valuable, and aligned with my voice. Avoid generic praise and strive for meaningful engagement.

Post content:
{post_content}

Summary: {summary}
Categories: {categories_str}

My persona:
{persona}

Return JSON array of exactly 3 comment strings:
["Comment 1", "Comment 2", "Comment 3"]

Only return the JSON array, no additional text."""

        try:
            response_text = self._call_with_retry(prompt, self.comment_model)
            # Try to extract JSON from response
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text

            # Parse JSON
            comments = json.loads(response_text)

            # Validate structure
            if not isinstance(comments, list):
                raise ValueError("Response must be a list")

            if len(comments) != 3:
                logger.warning(f"Expected 3 comments, got {len(comments)}")

            # Ensure we have exactly 3 comments
            while len(comments) < 3:
                comments.append("Error: Comment generation failed")

            comments = comments[:3]  # Take first 3

            logger.debug(f"Generated {len(comments)} comments")
            return comments

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text}")
            return [
                "Error: Failed to generate comments",
                "Error: Failed to generate comments",
                "Error: Failed to generate comments",
            ]
        except Exception as e:
            logger.error(f"Error generating comments: {e}")
            return [
                f"Error: {str(e)}",
                f"Error: {str(e)}",
                f"Error: {str(e)}",
            ]


if __name__ == "__main__":
    """Test LLM client."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    client = LLMClient()

    # Test post analysis
    sample_post = "Excited to share our new AI-powered product launch! This will revolutionize how teams collaborate."
    print("Testing post analysis...")
    analysis = client.analyze_post(sample_post)
    print(f"Summary: {analysis['summary']}")
    print(f"Categories: {analysis['categories']}")

    # Test comment generation
    persona = "I am a software engineer specializing in AI and automation."
    print("\nTesting comment generation...")
    comments = client.generate_comments(
        sample_post,
        analysis["summary"],
        analysis["categories"],
        persona,
    )
    for i, comment in enumerate(comments, 1):
        print(f"\nComment {i}:")
        print(comment)

