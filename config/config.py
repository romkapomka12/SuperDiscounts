import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import logger
import undetected_chromedriver as uc
import time
import random

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE_PATH = os.path.join(PROJECT_ROOT, "products.db")
FAVORITES_FILE_PATH = os.path.join(PROJECT_ROOT, "users_favorites.json")


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
]


def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",

    }


def setup_undetected_driver() -> webdriver.Chrome:
    try:
        logger.info("=" * 50)
        logger.info("Ініціалізація Chrome WebDriver")
        logger.info("Локальний запуск")

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")

        user_agent = random.choice(USER_AGENTS)
        options.add_argument(f"--user-agent={user_agent}")
        logger.debug(f"Використовується User-Agent: {user_agent}")

        driver = uc.Chrome(
            options=options,
            headless=False,
            use_subprocess=True
        )

        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                        """
            })

        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": user_agent,
            "platform": "Win32"
        })

        logger.info("Chrome WebDriver успішно ініціалізовано")
        return driver

    except Exception as e:
        logger.critical("Помилка ініціалізації WebDriver: %s", str(e), exc_info=True)
        raise
