import pytest
from pytest import fixture
from playwright.sync_api import BrowserContext
from playwright.sync_api import Browser, BrowserType, Playwright, sync_playwright


@pytest.fixture(scope="session") # session function
def context(browser):
    # Кастомный контекст (например, с куками или viewport)
    context = browser.new_context(
        viewport={"width": 1200, "height": 800},
        locale="ru-RU"
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    page = context.new_page()
    yield page
    if not page.is_closed():
        page.close()
