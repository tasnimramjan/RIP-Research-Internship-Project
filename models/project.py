import json
import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class ProjectModel:
    @staticmethod
    def get_all_posts(skill_filter=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.*, u.name as author_name, u.email as author_email, u.department, s.cgpa
        FROM project_posts p
        JOIN users u ON p.student_id = u.user_id
        LEFT JOIN students s ON p.student_id = s.student_id
        ORDER BY p.created_at DESC
        """)
        rows = cursor.fetchall()
        
        posts = []
        for r in rows:
            post = dict(r)
            skills = json.loads(post['required_skills'])
            post['required_skills'] = skills
            
            if skill_filter:
                sf = skill_filter.lower().strip()
                if not any(sf in sk.lower() for sk in skills):
                    continue
                    
            # Fetch existing teammates
            cursor.execute("""
            SELECT tm.*, u.name, u.email
            FROM project_teammates tm
            JOIN users u ON tm.student_id = u.user_id
            WHERE tm.post_id = ?
            """, (post['post_id'],))
            post['teammates'] = [dict(t) for t in cursor.fetchall()]
            
            posts.append(post)
            
        conn.close()
        return posts

    @staticmethod
    def create_post(student_id, idea_title, description, required_skills):
        conn = get_db()
        cursor = conn.cursor()
        post_id = "post_" + str(uuid.uuid4())[:6]
        
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(',') if s.strip()]
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO project_posts (post_id, student_id, idea_title, description, required_skills, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (post_id, student_id, idea_title, description, json.dumps(required_skills), now)
        )
        conn.commit()
        conn.close()
        return post_id

    @staticmethod
    def add_teammate(post_id, student_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM project_teammates WHERE post_id = ? AND student_id = ?", (post_id, student_id))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "message": "Already a member of this project team."}
            
        cursor.execute(
            "INSERT INTO project_teammates (post_id, student_id, status) VALUES (?, ?, ?)",
            (post_id, student_id, "Accepted")
        )
        conn.commit()
        conn.close()
        return {"success": True, "message": "Joined project team successfully."}
