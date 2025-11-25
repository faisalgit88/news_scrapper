import time
from playwright.sync_api import sync_playwright, TimeoutError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import Article, Source, init_db
from analyzer import analyze_article
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self, db_path=None):
        self.Session = init_db(db_path)
        self.session = self.Session()

    def should_scrape(self, url):
        """
        Decides if a URL should be scraped based on a blocklist and extensions.
        """
        # 1. Extension Filter
        skip_extensions = [
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp4', '.mp3', 
            '.zip', '.rar', '.exe', '.dmg', '.css', '.js', '.xml', '.json'
        ]
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False

        # 2. Blocklist Filter
        blocklist = [
            'login', 'signin', 'signup', 'register', 'auth', 'password', 
            'account', 'profile', 'user', 'settings', 'preferences',
            'contact', 'about', 'privacy', 'terms', 'tos', 'policy',
            'search', 'query', 'filter', 'sort', 'order',
            'cart', 'checkout', 'basket', 'shop',
            'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', # Social media
            'javascript:', 'mailto:', 'tel:',
            # Hacker News specific
            'vote?', 'hide?', 'submit', 'flag', 'reply', 'item?', 'from?', 'format=json'
        ]
        if any(keyword in url.lower() for keyword in blocklist):
            return False

        return True

    def _navigate(self, page, url, retries=3, timeout=30000):
        """
        Navigates to a URL with retry logic.
        """
        for i in range(retries):
            try:
                response = page.goto(url, timeout=timeout, wait_until='domcontentloaded')
                if response and response.status >= 400:
                    logger.warning(f"Failed to load {url}: Status {response.status}")
                    return False
                return True
            except TimeoutError:
                logger.warning(f"Timeout navigating to {url}. Retry {i+1}/{retries}")
            except Exception as e:
                logger.error(f"Error navigating to {url}: {e}")
                # Don't retry on non-timeout errors (like malformed URL) unless we want to be very aggressive
                return False
        logger.error(f"Failed to navigate to {url} after {retries} retries.")
        return False

    def scrape_source(self, source_id, on_progress=None):
        source = self.session.query(Source).filter_by(id=source_id).first()
        if not source:
            logger.error(f"Source with ID {source_id} not found.")
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage', # Essential for Docker/Cloud Run
                    '--single-process' # Helps in resource-constrained envs
                ]
            )
            context = browser.new_context()
            # Set a default timeout for the context
            context.set_default_timeout(60000)
            
            # Block unnecessary resources to speed up loading
            def route_intercept(route):
                if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
                    route.abort()
                else:
                    route.continue_()
            
            context.route("**/*", route_intercept)
            
            page = context.new_page()

            try:
                # Login if required
                if source.requires_login and source.login_url:
                    logger.info(f"Logging in to {source.name}...")
                    if self._navigate(page, source.login_url):
                        try:
                            page.fill(source.username_selector, source.username)
                            page.fill(source.password_selector, source.password)
                            if source.submit_selector:
                                page.click(source.submit_selector)
                            else:
                                page.keyboard.press('Enter')
                            page.wait_for_load_state('networkidle', timeout=30000)
                            logger.info("Login submitted.")
                        except Exception as e:
                            logger.error(f"Login failed for {source.name}: {e}")
                            # Continue anyway? Or return? Let's return as login is likely critical
                            return

                # Go to main page
                logger.info(f"Navigating to {source.url}...")
                if not self._navigate(page, source.url):
                    return

                # Find article links
                try:
                    links = page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                except Exception as e:
                    logger.error(f"Failed to extract links from {source.url}: {e}")
                    links = []
                
                unique_links = set(links)
                logger.info(f"Found {len(unique_links)} links.")

                new_articles_count = 0
                for link in unique_links:
                    if not link.startswith("http"): continue
                    
                    # Domain check
                    if not source.include_external:
                        if source.url not in link: continue 
                    
                    if not self.should_scrape(link):
                        # logger.info(f"Skipping filtered URL: {link}") # Reduce noise
                        continue
                    
                    if self.session.query(Article).filter_by(url=link).first():
                        continue

                    try:
                        # Visit article page
                        logger.info(f"Scraping article: {link}")
                        if not self._navigate(page, link, retries=2, timeout=20000):
                            continue
                            
                        content = page.content()
                        
                        # Analyze
                        analysis = analyze_article(link, html_content=content)
                        
                        if not analysis['title'] or len(analysis['text']) < 200:
                            continue

                        # Save to DB
                        new_article = Article(
                            title=analysis['title'],
                            url=link,
                            content=analysis['text'],
                            summary=analysis['summary'],
                            sentiment=analysis['sentiment'],
                            sentiment_score=analysis['sentiment_score'],
                            category=source.category,
                            source_id=source.id
                        )
                        self.session.add(new_article)
                        self.session.commit()
                        new_articles_count += 1
                        if on_progress:
                            on_progress()
                        
                    except Exception as e:
                        logger.error(f"Failed to scrape {link}: {e}")
                        continue
                
                logger.info(f"Scraping finished for {source.name}. Added {new_articles_count} new articles.")

            except Exception as e:
                logger.error(f"Error scraping {source.name}: {e}")
            finally:
                browser.close()

    def close(self):
        self.session.close()
