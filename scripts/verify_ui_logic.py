from app import get_articles
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database import init_db, Source, Article
from datetime import datetime, timedelta

# Initialize DB
Session = init_db()
session = Session()

# Ensure we have some data
if session.query(Article).count() == 0:
    print("No articles in DB. Skipping logic test.")
else:
    print("Testing get_articles logic...")
    
    # Test 1: No filters
    all_articles = get_articles()
    print(f"All articles: {len(all_articles)}")
    
    # Test 2: Sentiment Filter
    pos_articles = get_articles(sentiment_filter=["Positive"])
    print(f"Positive articles: {len(pos_articles)}")
    
    # Test 3: Source Filter (Mocking if needed, but let's try with existing)
    sources = session.query(Source).all()
    if sources:
        s_name = sources[0].name
        source_articles = get_articles(source_filter=[s_name])
        print(f"Articles from {s_name}: {len(source_articles)}")

    # Test 4: Date Range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_articles = get_articles(date_range=(start_date, end_date))
    print(f"Articles in last 30 days: {len(date_articles)}")

print("UI Logic Verification Complete.")
