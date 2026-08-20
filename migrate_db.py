import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rip_database.sqlite")

def migrate():
    if not os.path.exists(DB_PATH):
        print("DB does not exist.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(faculty)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'max_capacity' not in columns:
        print("Adding max_capacity column to faculty...")
        cursor.execute("ALTER TABLE faculty ADD COLUMN max_capacity INTEGER NOT NULL DEFAULT 5")
        
    if 'current_students' not in columns:
        print("Adding current_students column to faculty...")
        cursor.execute("ALTER TABLE faculty ADD COLUMN current_students INTEGER NOT NULL DEFAULT 0")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
