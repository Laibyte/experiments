"""LinkedIn authentication handler with cookie persistence."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.services.browser_manager import BrowserManager

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

COOKIES_FILE = Path("data/cookies.json")
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
FEED_SELECTOR = ".scaffold-finite-scroll"


class AuthHandler:
    """Handles LinkedIn authentication and session persistence."""

    def __init__(self, headless: bool = False) -> None:
        """Initialize authentication handler.

        Args:
            headless: Run browser in headless mode.
        """
        self.browser_manager = BrowserManager(headless=headless)
        self.driver: WebDriver | None = None

    def _load_cookies(self) -> list[dict] | None:
        """Load cookies from file.

        Returns:
            List of cookie dictionaries or None if file doesn't exist.
        """
        if not COOKIES_FILE.exists():
            logger.info("No cookies file found")
            return None

        try:
            with COOKIES_FILE.open(encoding="utf-8") as f:
                cookies = json.load(f)
            logger.info(f"Loaded {len(cookies)} cookies from file")
            return cookies
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load cookies: {e}")
            return None

    def _save_cookies(self) -> None:
        """Save cookies to file."""
        if not self.driver:
            raise RuntimeError("Browser not started")

        cookies = self.driver.get_cookies()
        COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)

        with COOKIES_FILE.open("w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        logger.info(f"Saved {len(cookies)} cookies to {COOKIES_FILE}")

    def _inject_cookies(self, cookies: list[dict]) -> None:
        """Inject cookies into browser session.

        Args:
            cookies: List of cookie dictionaries.
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        # Navigate to LinkedIn first to set domain
        self.browser_manager.navigate_to("https://www.linkedin.com")

        for cookie in cookies:
            try:
                # Remove 'expiry' if present (Selenium doesn't accept it)
                cookie.pop("expiry", None)
                self.driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"Failed to add cookie {cookie.get('name')}: {e}")

        logger.info(f"Injected {len(cookies)} cookies")

    def _is_logged_in(self) -> bool:
        """Check if user is logged in to LinkedIn.

        Returns:
            True if logged in, False otherwise.
        """
        if not self.driver:
            return False

        try:
            self.browser_manager.wait_for_element(FEED_SELECTOR, timeout=5)
            logger.info("Login validated: feed element found")
            return True
        except Exception:
            logger.info("Login validation failed: feed element not found")
            return False

    def authenticate(self) -> "WebDriver":
        """Authenticate with LinkedIn, using cookies if available.

        Returns:
            WebDriver instance with authenticated session.
        """
        self.driver = self.browser_manager.start_browser()

        # Try to load existing cookies
        cookies = self._load_cookies()
        if cookies:
            self._inject_cookies(cookies)
            self.browser_manager.navigate_to(LINKEDIN_FEED_URL)

            # Validate session
            if self._is_logged_in():
                logger.info("Successfully authenticated using saved cookies")
                return self.driver

            logger.warning("Saved cookies invalid, requesting new login")

        # Manual login required
        logger.info("No valid cookies found, manual login required")
        self.browser_manager.navigate_to(LINKEDIN_FEED_URL)
        print("\n" + "=" * 60)
        print("Please log in to LinkedIn in the browser window")
        print("After logging in, press Enter to continue...")
        print("=" * 60 + "\n")
        input()

        # Validate login
        if not self._is_logged_in():
            raise RuntimeError("Login validation failed. Please ensure you're logged in.")

        # Save cookies for next time
        self._save_cookies()
        logger.info("Authentication successful, cookies saved")

        return self.driver

    def close(self) -> None:
        """Close browser session."""
        self.browser_manager.close_browser()
        self.driver = None


if __name__ == "__main__":
    """Test authentication handler."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    handler = AuthHandler()
    try:
        handler.authenticate()
        print("\nAuthentication test successful!")
        input("Press Enter to close browser...")
    finally:
        handler.close()

