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
# 16. Events Hub
c.execute("""
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    organizer TEXT NOT NULL,
    event_date TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    registration_link TEXT,
    created_at TEXT NOT NULL
)
""")

# 17. Admin Logs & Verification
c.execute("""
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    target_user TEXT,
    timestamp TEXT NOT NULL
)
""")

# 18. Notifications
c.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    notif_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT DEFAULT 'General',
    is_read INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
)
""")

# 19. Dashboard Tasks
c.execute("""
CREATE TABLE IF NOT EXISTS user_tasks (
    task_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    task_title TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT DEFAULT 'Pending'
)
""")

# 20. Chatbot Knowledgebase
c.execute("""
CREATE TABLE IF NOT EXISTS faq_chatbot (
    faq_id TEXT PRIMARY KEY,
    keywords TEXT NOT NULL,
    answer TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Migration complete.")
