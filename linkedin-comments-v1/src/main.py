"""Main CLI entry point for LinkedIn Comment Automation."""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from src.features.auth_handler import AuthHandler
from src.features.comment_generator import CommentGenerator
from src.features.feed_collector import FeedCollector
from src.features.post_analyzer import PostAnalyzer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def setup_logging(log_file: Path | None = None) -> None:
    """Configure logging for the application.

    Args:
        log_file: Optional log file path.
    """
    handlers = [logging.StreamHandler()]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def cmd_auth(args: argparse.Namespace) -> None:
    """Handle auth command.

    Args:
        args: Command line arguments.
    """
    print("=" * 60)
    print("LinkedIn Authentication")
    print("=" * 60)

    handler = AuthHandler(headless=args.headless)
    try:
        handler.authenticate()
        print("\n✓ Authentication successful!")
        print("Cookies saved for future use.")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        print(f"\n✗ Authentication failed: {e}")
        sys.exit(1)
    finally:
        handler.close()


def cmd_collect(args: argparse.Namespace) -> None:
    """Handle collect command.

    Args:
        args: Command line arguments.
    """
    print("=" * 60)
    print(f"Collecting {args.num_posts} LinkedIn Posts")
    print("=" * 60)

    collector = FeedCollector(headless=args.headless)
    try:
        posts = collector.collect_posts(num_posts=args.num_posts)
        output_file = collector.save_posts(posts)
        print(f"\n✓ Successfully collected {len(posts)} posts")
        print(f"Saved to: {output_file}")
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        print(f"\n✗ Collection failed: {e}")
        sys.exit(1)
    finally:
        collector.close()


def cmd_download(args: argparse.Namespace) -> None:
    """Handle download command.

    Args:
        args: Command line arguments.
    """
    print("=" * 60)
    print(f"Downloading Post from URL: {args.url}")
    print("=" * 60)

    collector = FeedCollector(headless=args.headless)
    try:
        post_data = collector.download_post_from_url(args.url)
        if post_data:
            posts = [post_data]
            output_file = collector.save_posts(posts)
            print(f"\n✓ Successfully downloaded post")
            print(f"Saved to: {output_file}")
        else:
            print("\n✗ Failed to download post")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        print(f"\n✗ Download failed: {e}")
        sys.exit(1)
    finally:
        collector.close()


def cmd_analyze(args: argparse.Namespace) -> None:
    """Handle analyze command.

    Args:
        args: Command line arguments.
    """
    input_file = Path(args.input_file)
    print("=" * 60)
    print(f"Analyzing Posts from {input_file}")
    print("=" * 60)

    analyzer = PostAnalyzer(max_workers=args.max_workers)
    try:
        output_file = analyzer.run(input_file)
        print("\n✓ Analysis complete")
        print(f"Output file: {output_file}")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\n✗ Analysis failed: {e}")
        sys.exit(1)


def cmd_generate(args: argparse.Namespace) -> None:
    """Handle generate command.

    Args:
        args: Command line arguments.
    """
    input_file = Path(args.input_file)
    print("=" * 60)
    print(f"Generating Comments from {input_file}")
    print("=" * 60)

    generator = CommentGenerator(max_workers=args.max_workers)
    try:
        saved_files = generator.run(input_file)
        print("\n✓ Comment generation complete")
        print(f"Generated {len(saved_files)} markdown files")
    except Exception as e:
        logger.error(f"Comment generation failed: {e}")
        print(f"\n✗ Comment generation failed: {e}")
        sys.exit(1)


def cmd_debug(args: argparse.Namespace) -> None:
    """Handle debug command to inspect post structure.

    Args:
        args: Command line arguments.
    """
    print("=" * 60)
    print("Debugging LinkedIn Post Structure")
    print("=" * 60)

    collector = FeedCollector(headless=args.headless)
    try:
        debug_file = collector.debug_post_structure(num_posts=args.num_posts)
        print(f"\n✓ Debug data collected")
        print(f"Debug JSON: {debug_file}")
        print(f"Debug HTML: {debug_file.parent / debug_file.name.replace('structure', 'html').replace('.json', '.html')}")
        print("\nInspect these files to understand the post structure.")
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        print(f"\n✗ Debug failed: {e}")
        sys.exit(1)
    finally:
        collector.close()


def cmd_full(args: argparse.Namespace) -> None:
    """Handle full pipeline command.

    Args:
        args: Command line arguments.
    """
    print("=" * 60)
    print("LinkedIn Comment Automation - Full Pipeline")
    print("=" * 60)
    print(f"Collecting {args.num_posts} posts...")
    print()

    # Phase I: Authentication
    print("[Phase I] Authentication...")
    handler = AuthHandler(headless=args.headless)
    try:
        handler.authenticate()
        print("✓ Authentication successful")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        print(f"✗ Authentication failed: {e}")
        handler.close()
        sys.exit(1)

    # Phase II: Collect posts
    print("\n[Phase II] Collecting posts...")
    collector = FeedCollector(headless=args.headless)
    collector.auth_handler = handler  # Reuse authenticated session
    collector.driver = handler.driver

    try:
        posts = collector.collect_posts(num_posts=args.num_posts)
        posts_file = collector.save_posts(posts)
        print(f"✓ Collected {len(posts)} posts")
        print(f"  Saved to: {posts_file}")
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        print(f"✗ Collection failed: {e}")
        handler.close()
        sys.exit(1)
    finally:
        handler.close()

    # Phase III: Analyze posts
    print("\n[Phase III] Analyzing posts...")
    analyzer = PostAnalyzer(max_workers=args.max_workers)
    try:
        analyzed_file = analyzer.run(posts_file)
        print("✓ Analysis complete")
        print(f"  Saved to: {analyzed_file}")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"✗ Analysis failed: {e}")
        sys.exit(1)

    # Phase IV: Generate comments
    print("\n[Phase IV] Generating comments...")
    generator = CommentGenerator(max_workers=args.max_workers)
    try:
        saved_files = generator.run(analyzed_file)
        print("✓ Comment generation complete")
        print(f"  Generated {len(saved_files)} markdown files")
    except Exception as e:
        logger.error(f"Comment generation failed: {e}")
        print(f"✗ Comment generation failed: {e}")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    print(f"Posts collected: {len(posts)}")
    print(f"Posts file: {posts_file}")
    print(f"Analyzed file: {analyzed_file}")
    print(f"Comment files: {len(saved_files)} files in data/posts_processed/")
    print("=" * 60)


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="LinkedIn Comment Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test authentication
  python -m src.main auth

  # Collect 20 posts
  python -m src.main collect --num-posts 20

  # Download a post from URL
  python -m src.main download --url https://www.linkedin.com/feed/update/...

  # Analyze collected posts (with concurrency)
  python -m src.main analyze --input-file data/post_2025-11-07-14-30-00.json --max-workers 5

  # Generate comments (with concurrency)
  python -m src.main generate --input-file data/analyzed/post_analyzed_2025-11-07-15-00-00.json --max-workers 5

  # Run full pipeline
  python -m src.main full --num-posts 20
  python -m src.main full --num-posts 20 --max-workers 5

  # Debug post structure
  python -m src.main debug --num-posts 3
        """,
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with LinkedIn")
    auth_parser.set_defaults(func=cmd_auth)

    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect posts from LinkedIn feed")
    collect_parser.add_argument(
        "--num-posts",
        type=int,
        default=10,
        help="Number of posts to collect (default: 10)",
    )
    collect_parser.set_defaults(func=cmd_collect)

    # Download command
    download_parser = subparsers.add_parser(
        "download", help="Download a single post from a LinkedIn URL"
    )
    download_parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="LinkedIn post URL",
    )
    download_parser.set_defaults(func=cmd_download)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze posts using LLM")
    analyze_parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Input JSON file with posts",
    )
    analyze_parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of concurrent workers (default: auto)",
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate comment suggestions")
    generate_parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Input JSON file with analyzed posts",
    )
    generate_parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of concurrent workers (default: auto)",
    )
    generate_parser.set_defaults(func=cmd_generate)

    # Full command
    full_parser = subparsers.add_parser("full", help="Run full pipeline")
    full_parser.add_argument(
        "--num-posts",
        type=int,
        default=10,
        help="Number of posts to collect (default: 10)",
    )
    full_parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of concurrent workers for analysis and generation (default: auto)",
    )
    full_parser.set_defaults(func=cmd_full)

    # Debug command
    debug_parser = subparsers.add_parser("debug", help="Debug post structure to inspect DOM/JSON")
    debug_parser.add_argument(
        "--num-posts",
        type=int,
        default=1,
        help="Number of posts to debug (default: 1)",
    )
    debug_parser.set_defaults(func=cmd_debug)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup logging
    log_file = Path(f"data/logs/run-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log")
    setup_logging(log_file)

    # Run command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
