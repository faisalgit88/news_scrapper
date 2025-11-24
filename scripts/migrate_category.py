import sqlite3
import os
import sys

# Add src to path to import database models if needed (though we are doing raw SQL here)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def migrate_category():
    # Path to database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'news_data.db')
    
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Add category to sources
    try:
        print("Adding 'category' column to 'sources' table...")
        cursor.execute("ALTER TABLE sources ADD COLUMN category TEXT")
        print("Success.")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("Column 'category' already exists in 'sources'.")
        else:
            print(f"Error adding column to sources: {e}")

    # 2. Add category to articles
    try:
        print("Adding 'category' column to 'articles' table...")
        cursor.execute("ALTER TABLE articles ADD COLUMN category TEXT")
        print("Success.")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("Column 'category' already exists in 'articles'.")
        else:
            print(f"Error adding column to articles: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_category()
