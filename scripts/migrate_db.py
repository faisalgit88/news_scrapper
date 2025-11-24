import sqlite3

def migrate():
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'news_data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Attempting to add 'include_external' column to 'sources' table...")
        cursor.execute("ALTER TABLE sources ADD COLUMN include_external BOOLEAN DEFAULT 0")
        conn.commit()
        print("Migration successful.")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("Column already exists. Skipping.")
        else:
            print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
