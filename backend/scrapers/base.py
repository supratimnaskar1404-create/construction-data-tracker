from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time

class BaseScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def fetch_dynamic_content(self, url, wait_for_selector=None):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector)
            else:
                time.sleep(2)  # fallback wait
            content = page.content()
            browser.close()
            return content

    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')
