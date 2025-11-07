"""Browser management service using Selenium."""

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages Selenium WebDriver instances."""

    def __init__(self, headless: bool = False) -> None:
        """Initialize browser manager.

        Args:
            headless: Run browser in headless mode.
        """
        self.headless = headless
        self.driver: WebDriver | None = None

    def start_browser(self) -> WebDriver:
        """Start a new browser instance.

        Returns:
            WebDriver instance.
        """
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Browser started successfully")
        return self.driver

    def navigate_to(self, url: str) -> None:
        """Navigate to a URL.

        Args:
            url: URL to navigate to.
        """
        if not self.driver:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        self.driver.get(url)
        logger.info(f"Navigated to {url}")

    def wait_for_element(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
        timeout: int = 10,
    ) -> "WebElement":
        """Wait for an element to be present.

        Args:
            selector: CSS selector or XPath.
            by: Locator strategy (default: CSS_SELECTOR).
            timeout: Maximum wait time in seconds.

        Returns:
            WebElement when found.

        Raises:
            TimeoutException: If element not found within timeout.
        """
        if not self.driver:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.presence_of_element_located((by, selector)))
        logger.debug(f"Element found: {selector}")
        return element

    def close_browser(self) -> None:
        """Close the browser instance."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")

    @contextmanager
    def browser_context(self):
        """Context manager for browser lifecycle.

        Yields:
            WebDriver instance.
        """
        driver = self.start_browser()
        try:
            yield driver
        finally:
            self.close_browser()

    def __enter__(self) -> "BrowserManager":
        """Enter context manager."""
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.close_browser()


if __name__ == "__main__":
    """Test browser manager."""
    logging.basicConfig(level=logging.INFO)
    with BrowserManager() as manager:
        manager.navigate_to("https://www.google.com")
        input("Press Enter to close browser...")

