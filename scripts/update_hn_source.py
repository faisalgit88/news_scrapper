import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database import init_db, Source

def update_hn():
    Session = init_db()
    session = Session()
    
    hn = session.query(Source).filter_by(name="Hacker News").first()
    if hn:
        print(f"Updating {hn.name}...")
        hn.include_external = True
        session.commit()
        print("Updated 'include_external' to True.")
    else:
        print("Hacker News source not found.")

if __name__ == "__main__":
    update_hn()
