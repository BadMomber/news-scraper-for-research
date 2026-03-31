import asyncio
import logging

from playwright.async_api import Browser, BrowserContext, Page

from .models import ZeitArticle, ZeitSearchResult
from .search import _dismiss_cookie_banner, RATE_LIMIT_SECONDS, MAX_RETRIES, BACKOFF_SECONDS

logger = logging.getLogger(__name__)

LOGIN_URL = "https://meine.zeit.de/anmelden"


async def _login(page: Page, username: str, password: str) -> bool:
    """Log in to zeit.de and return True on success."""
    try:
        await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        await _dismiss_cookie_banner(page)

        # Keycloak login form at login.zeit.de
        await page.fill("#username", username)
        await page.fill("#password", password)

        # FriendlyCaptcha runs a proof-of-work that enables the submit button.
        # Playwright's click auto-waits for enabled state; allow up to 60s.
        await page.click("input[name='login']", timeout=60000)

        # Wait for redirect after login
        await page.wait_for_load_state("domcontentloaded", timeout=15000)

        # Check for success: redirect away from login page
        if "login.zeit.de" not in page.url:
            logger.info("zeit.de Login erfolgreich")
            return True

        # Alternative: check for logged-in indicator
        logout_link = await page.query_selector("a[href*='abmelden'], a[href*='logout']")
        if logout_link:
            logger.info("zeit.de Login erfolgreich")
            return True

        logger.warning("zeit.de Login fehlgeschlagen — weiter ohne Login")
        return False

    except Exception as e:
        logger.warning("zeit.de Login fehlgeschlagen: %s — weiter ohne Login", e)
        return False


async def _scrape_with_context(
    context: BrowserContext,
    results: list[ZeitSearchResult],
    search_terms: str,
    close_context_per_article: bool,
    browser: Browser,
) -> list[ZeitArticle]:
    """Scrape articles using the given context strategy."""
    articles: list[ZeitArticle] = []

    for i, result in enumerate(results):
        logger.info("Scrape %d/%d: %s", i + 1, len(results), result.url)

        if close_context_per_article:
            # Fresh context per article (no-login mode)
            context = await browser.new_context()

        page = await context.new_page()

        try:
            try:
                await _navigate_with_retry(page, result.url)
            except Exception as e:
                logger.error("Überspringe Artikel '%s': %s", result.title, e)
                continue

            await _dismiss_cookie_banner(page)

            author = await _extract_author(page)
            body_text = await _extract_body_text(page)
            char_count = len(body_text)

            articles.append(ZeitArticle(
                date=result.date,
                url=result.url,
                title=result.title,
                author=author,
                char_count=char_count,
                search_terms=search_terms,
                is_zplus=result.is_zplus,
                body_text=body_text,
            ))
        finally:
            await page.close()
            if close_context_per_article:
                await context.close()

        if i < len(results) - 1:
            await asyncio.sleep(RATE_LIMIT_SECONDS)

    return articles


async def create_logged_in_context(browser: Browser, username: str, password: str) -> BrowserContext | None:
    """Create a browser context logged in to zeit.de.

    Returns the logged-in context, or None if login fails.
    """
    context = await browser.new_context()
    page = await context.new_page()
    success = await _login(page, username, password)
    await page.close()

    if success:
        return context

    await context.close()
    return None


async def scrape_articles(
    browser: Browser,
    results: list[ZeitSearchResult],
    keyword_pair: list[str],
    logged_in_context: BrowserContext | None = None,
) -> list[ZeitArticle]:
    """Scrape article details for each zeit.de search result.

    With logged_in_context: reuse that context for all articles (Z+ full text).
    Without: fresh context per article to avoid metered paywall.
    """
    search_terms = "+".join(keyword_pair)

    if logged_in_context is not None:
        articles = await _scrape_with_context(
            logged_in_context, results, search_terms,
            close_context_per_article=False, browser=browser,
        )
    else:
        articles = await _scrape_with_context(
            await browser.new_context(), results, search_terms,
            close_context_per_article=True, browser=browser,
        )

    logger.info(
        "Scrape '%s': %d/%d Artikel erfolgreich",
        search_terms, len(articles), len(results),
    )
    return articles


async def _navigate_with_retry(page: Page, url: str) -> None:
    """Navigate to URL with retry and exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                logger.error("Navigation fehlgeschlagen nach %d Versuchen: %s", MAX_RETRIES, url)
                raise
            backoff = BACKOFF_SECONDS[attempt]
            logger.warning(
                "Navigation fehlgeschlagen (Versuch %d/%d), warte %ds: %s",
                attempt + 1, MAX_RETRIES, backoff, e,
            )
            await asyncio.sleep(backoff)


async def _extract_author(page: Page) -> str:
    """Extract author name(s) from zeit.de article page.

    zeit.de structure:
        <a href="/autoren/X/Name/index" title="Full Name" rel="author">
          <span itemprop="name">shortname</span>
        </a>

    The title attribute contains the full name, innerText may be a shortcode.
    """
    author_links = await page.query_selector_all("a[href*='/autoren/'][rel='author']")

    if not author_links:
        # Fallback: any link to /autoren/
        author_links = await page.query_selector_all("a[href*='/autoren/']")

    seen = set()
    authors = []
    for link in author_links:
        # Prefer title attribute (full name) over innerText (may be shortcode)
        title_attr = await link.get_attribute("title")
        name = title_attr.strip() if title_attr else (await link.inner_text()).strip()
        if name and name not in seen:
            seen.add(name)
            authors.append(name)

    return ", ".join(authors)


async def _extract_body_text(page: Page) -> str:
    """Extract article body text with Markdown-style headings from zeit.de.

    Uses <p> and <h2>/<h3> elements within <article>. For Z+ articles,
    this returns only the visible teaser text.
    """
    elements = await page.query_selector_all("article p, article h2, article h3")

    texts = []
    for el in elements:
        tag = await el.evaluate("el => el.tagName")
        text = (await el.inner_text()).strip()
        if not text:
            continue
        if tag == "H2":
            texts.append(f"\n## {text}")
        elif tag == "H3":
            texts.append(f"\n### {text}")
        else:
            texts.append(text)

    return "\n".join(texts).strip()
