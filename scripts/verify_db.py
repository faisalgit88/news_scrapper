import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database import init_db, Source, Article

Session = init_db()
session = Session()

source = session.query(Source).filter_by(name="Bad Source").first()
if source:
    print(f"Source found: {source.name}")
    articles = session.query(Article).filter_by(source_id=source.id).count()
    print(f"Articles found: {articles}")
else:
    print("Source not found.")
