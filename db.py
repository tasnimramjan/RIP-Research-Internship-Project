import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rip_database.sqlite")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users Table (Base)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        department TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Student', 'Faculty', 'Admin')),
        status TEXT DEFAULT 'Active'
    )
    """)
    
    # 2. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        cgpa REAL NOT NULL,
        research_interests TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    # 3. Faculty Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        faculty_id TEXT PRIMARY KEY,
        designation TEXT NOT NULL,
        h_index INTEGER NOT NULL DEFAULT 0,
        research_domains TEXT NOT NULL,
        remaining_slots INTEGER NOT NULL DEFAULT 5,
        min_cgpa_req REAL DEFAULT 3.0,
        thesis_available INTEGER DEFAULT 1,
        FOREIGN KEY (faculty_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    # 4. Admin Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        admin_id TEXT PRIMARY KEY,
        admin_level TEXT NOT NULL DEFAULT 'SuperAdmin',
        FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    # 5. Research Labs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_labs (
        lab_id TEXT PRIMARY KEY,
        lab_name TEXT NOT NULL,
        focus_area TEXT NOT NULL,
        facilities TEXT NOT NULL,
        faculty_id TEXT NOT NULL,
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
    )
    """)
    
    # 6. RA Opportunities in Labs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ra_opportunities (
        ra_id TEXT PRIMARY KEY,
        lab_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        stipend TEXT,
        deadline TEXT,
        FOREIGN KEY (lab_id) REFERENCES research_labs(lab_id)
    )
    """)
    
    # 7. Ongoing Projects in Labs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_projects (
        project_id TEXT PRIMARY KEY,
        lab_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        FOREIGN KEY (lab_id) REFERENCES research_labs(lab_id)
    )
    """)
    
    # 8. Internship Opportunities
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS internship_opportunities (
        opportunity_id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        title TEXT NOT NULL,
        requirements TEXT NOT NULL,
        min_cgpa REAL DEFAULT 3.0,
        department TEXT,
        deadline TEXT NOT NULL,
        contact_email TEXT,
        contact_phone TEXT,
        external_url TEXT
    )
    """)
    
    # 9. Internship Applications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS internship_applications (
        application_id TEXT PRIMARY KEY,
        opportunity_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Shortlisted', 'Accepted', 'Rejected')),
        applied_at TEXT NOT NULL,
        FOREIGN KEY (opportunity_id) REFERENCES internship_opportunities(opportunity_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    
    # 10. Project Posts (Teammate Finder)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_posts (
        post_id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,
        idea_title TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    
    # 11. Project Teammates
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_teammates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        status TEXT DEFAULT 'Accepted',
        FOREIGN KEY (post_id) REFERENCES project_posts(post_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    
    # 12. Research Papers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_papers (
        paper_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        authors TEXT NOT NULL,
        domain TEXT NOT NULL,
        publication_year INTEGER NOT NULL,
        abstract TEXT NOT NULL,
        vector_embedding TEXT NOT NULL,
        doi TEXT,
        download_url TEXT
    )
    """)
    
    # 13. Discussion Threads
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discussion_threads (
        thread_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('Thesis Discussions', 'Project Discussions', 'Internship Discussions', 'Defense Preparation', 'General Academic Discussions')),
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    # 14. Forum Comments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forum_comments (
        comment_id TEXT PRIMARY KEY,
        thread_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (thread_id) REFERENCES discussion_threads(thread_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    # 15. Forum Reactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forum_reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        reaction_type TEXT NOT NULL,
        UNIQUE(thread_id, user_id, reaction_type),
        FOREIGN KEY (thread_id) REFERENCES discussion_threads(thread_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    # 16. Thread Reminders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thread_reminders (
        reminder_id TEXT PRIMARY KEY,
        thread_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        remind_at TEXT NOT NULL,
        note TEXT,
        is_triggered INTEGER DEFAULT 0,
        FOREIGN KEY (thread_id) REFERENCES discussion_threads(thread_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    # 17. Thesis Groups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thesis_groups (
        group_id TEXT PRIMARY KEY,
        group_name TEXT NOT NULL,
        topic TEXT NOT NULL,
        description TEXT NOT NULL,
        creator_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (creator_id) REFERENCES students(student_id)
    )
    """)
    
    # 18. Thesis Group Members
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thesis_group_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        joined_at TEXT NOT NULL,
        UNIQUE(group_id, student_id),
        FOREIGN KEY (group_id) REFERENCES thesis_groups(group_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    
    # 19. Chat Messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        message_id TEXT PRIMARY KEY,
        sender_id TEXT NOT NULL,
        receiver_id TEXT,
        group_id TEXT,
        message_text TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (sender_id) REFERENCES users(user_id)
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
