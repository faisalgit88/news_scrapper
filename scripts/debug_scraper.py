import logging
from database import init_db, Source
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from scraper import NewsScraper

# Configure logging to write to a file
root_logger = logging.getLogger()
file_handler = logging.FileHandler("scraper_debug.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(file_handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

def debug_scraper():
    Session = init_db()
    session = Session()
    
    sources = session.query(Source).all()
    if not sources:
        print("No sources found in database.")
        return

    print(f"Found {len(sources)} sources. Starting scrape...")
    
    scraper = NewsScraper()
    for source in sources:
        print(f"Scraping {source.name} ({source.url})...")
        try:
            scraper.scrape_source(source.id)
        except Exception as e:
            logger.error(f"CRITICAL FAILURE for {source.name}: {e}", exc_info=True)
            
    scraper.close()
    print("Scraping complete. Check scraper_debug.log for details.")

if __name__ == "__main__":
    debug_scraper()
