import streamlit
import playwright
try:
    Session = init_db()
    session = Session()
    print("Database initialized successfully.")
    
    # Check if we can query
    count = session.query(Source).count()
    print(f"Source count: {count}")
    
except Exception as e:
    print(f"Database error: {e}")
