import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rip_database.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check existing columns
cols = [r[1] for r in c.execute("PRAGMA table_info(users)")]
print("Current columns:", cols)

# Add status column if missing
if "status" not in cols:
    c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Active'")
    conn.commit()
    print("Added 'status' column to users table.")
else:
    print("'status' column already exists.")

# Verify
cols_after = [r[1] for r in c.execute("PRAGMA table_info(users)")]
print("Updated columns:", cols_after)
conn.close()
print("Migration complete.")
