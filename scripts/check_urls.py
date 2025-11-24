import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database import init_db, Source, Article

def list_urls():
    Session = init_db()
    session = Session()

    print("--- SOURCES ---")
    sources = session.query(Source).all()
    for s in sources:
        print(f"ID: {s.id} | Name: {s.name} | URL: {s.url} | External: {s.include_external}")

    print("\n--- SCRAPED ARTICLES ---")
    articles = session.query(Article).all()
    for a in articles:
        print(f"Source: {a.source.name} | Title: {a.title} | URL: {a.url}")
    
    print(f"\nTotal Articles: {len(articles)}")

if __name__ == "__main__":
    list_urls()
