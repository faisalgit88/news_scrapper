import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database import init_db, Source, Article
from scraper import NewsScraper
import logging

# Configure logging to see scraper output
logging.basicConfig(level=logging.INFO)

def test_error_handling():
    Session = init_db()
    session = Session()

    # 1. Add a Bad Source
    source_name = "Bad Source"
    source = session.query(Source).filter_by(name=source_name).first()
    if not source:
        print(f"Adding test source: {source_name}")
        source = Source(
            name=source_name,
            url="http://this-domain-does-not-exist-12345.com", # Non-existent URL
            requires_login=False
        )
        session.add(source)
        session.commit()
    else:
        print(f"Test source '{source_name}' already exists.")

    # 2. Run Scraper
    print(f"Scraping source: {source.name} ({source.url})")
    scraper = NewsScraper()
    try:
        # This should not crash, but log errors/retries
        scraper.scrape_source(source.id)
        print("Scraper finished execution (as expected).")
    except Exception as e:
        print(f"Scraper CRASHED: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_error_handling()
