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
        SELECT p.*, u.name as author_name, u.email as author_email, u.role as author_role, u.department, s.cgpa
        FROM project_posts p
        JOIN users u ON p.student_id = u.user_id
        LEFT JOIN students s ON p.student_id = s.student_id
        ORDER BY p.created_at DESC
        """)
        rows = cursor.fetchall()
        
        posts = []
        for r in rows:
            post = dict(r)
            try:
                skills = json.loads(post['required_skills'])
            except Exception:
                skills = [s.strip() for s in str(post['required_skills']).split(',') if s.strip()]
            post['required_skills'] = skills
            
            if skill_filter:
                sf = skill_filter.lower().strip()
                if not any(sf in sk.lower() for sk in skills):
                    continue
                    
            # Fetch all teammates and requests
            cursor.execute("""
            SELECT tm.*, u.name, u.email, u.role, u.department
            FROM project_teammates tm
            JOIN users u ON tm.student_id = u.user_id
            WHERE tm.post_id = ?
            """, (post['post_id'],))
            all_records = [dict(t) for t in cursor.fetchall()]
            
            post['teammates'] = [t for t in all_records if t['status'] == 'Accepted']
            post['pending_requests'] = [t for t in all_records if t['status'] == 'Pending']
            
            posts.append(post)
            
        conn.close()
        return posts

    @staticmethod
    def get_user_join_requests(user_id):
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Incoming requests for projects created by this user
        cursor.execute("""
            SELECT tm.id as request_id, tm.post_id, tm.student_id as applicant_id, tm.status,
                   p.idea_title, u.name as applicant_name, u.email as applicant_email, u.department as applicant_dept
            FROM project_teammates tm
            JOIN project_posts p ON tm.post_id = p.post_id
            JOIN users u ON tm.student_id = u.user_id
            WHERE p.student_id = ? AND tm.status = 'Pending'
            ORDER BY tm.id DESC
        """, (user_id,))
        incoming = [dict(r) for r in cursor.fetchall()]

        # 2. Outgoing requests sent by this user
        cursor.execute("""
            SELECT tm.id as request_id, tm.post_id, tm.student_id as applicant_id, tm.status,
                   p.idea_title, u.name as creator_name
            FROM project_teammates tm
            JOIN project_posts p ON tm.post_id = p.post_id
            JOIN users u ON p.student_id = u.user_id
            WHERE tm.student_id = ?
            ORDER BY tm.id DESC
        """, (user_id,))
        outgoing = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return {
            "incoming": incoming,
            "outgoing": outgoing,
            "pending_count": len(incoming)
        }

    @staticmethod
    def create_post(user_id, idea_title, description, required_skills):
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, role FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user or user['role'] != 'Student':
            conn.close()
            return None
            
        post_id = "post_" + str(uuid.uuid4())[:6]
        
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(',') if s.strip()]
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO project_posts (post_id, student_id, idea_title, description, required_skills, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (post_id, user_id, idea_title, description, json.dumps(required_skills), now)
        )
        conn.commit()
        conn.close()
        return post_id

    @staticmethod
    def add_teammate(post_id, user_id):
        if not post_id or not user_id:
            return {"success": False, "message": "Post ID and User ID required."}
            
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, role, name FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return {"success": False, "message": "User not found."}
            
        if user['role'] != 'Student':
            conn.close()
            return {"success": False, "message": f"{user['role']}s cannot join project teams. Only students can join."}
        
        cursor.execute("SELECT * FROM project_posts WHERE post_id = ?", (post_id,))
        post = cursor.fetchone()
        if not post:
            conn.close()
            return {"success": False, "message": "Project post not found."}
            
        if post['student_id'] == user_id:
            conn.close()
            return {"success": False, "message": "You are the creator of this project post."}
            
        cursor.execute("SELECT * FROM project_teammates WHERE post_id = ? AND student_id = ?", (post_id, user_id))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            if existing['status'] == 'Accepted':
                return {"success": False, "message": "Already a member of this project team."}
            elif existing['status'] == 'Pending':
                return {"success": False, "message": "You already have a pending join request for this project."}
            
        cursor.execute(
            "INSERT INTO project_teammates (post_id, student_id, status) VALUES (?, ?, ?)",
            (post_id, user_id, "Pending")
        )
        
        # Send notification to project creator
        creator_id = post['student_id']
        applicant_name = user['name']
        notif_id = "notif_" + str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO notifications (notification_id, user_id, type, title, message, reference_id, sender_id, is_read, created_at)
            VALUES (?, ?, 'join_request', ?, ?, ?, ?, 0, ?)
        """, (
            notif_id,
            creator_id,
            f"Join Request: {post['idea_title']}",
            f"{applicant_name} requested to join your project '{post['idea_title']}'.",
            post_id,
            user_id,
            now
        ))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Join request sent! The project creator will review your request."}

    @staticmethod
    def respond_to_join_request(post_id, applicant_id, creator_id, action):
        if not post_id or not applicant_id or not creator_id:
            return {"success": False, "message": "Post ID, Applicant ID, and Creator ID are required."}

        conn = get_db()
        cursor = conn.cursor()

        # Verify post and creator ownership
        cursor.execute("SELECT * FROM project_posts WHERE post_id = ?", (post_id,))
        post = cursor.fetchone()
        if not post or post['student_id'] != creator_id:
            conn.close()
            return {"success": False, "message": "Unauthorized or project post not found."}

        cursor.execute("SELECT name FROM users WHERE user_id = ?", (creator_id,))
        c_row = cursor.fetchone()
        creator_name = c_row['name'] if c_row else "Project Creator"

        cursor.execute("SELECT name FROM users WHERE user_id = ?", (applicant_id,))
        a_row = cursor.fetchone()
        applicant_name = a_row['name'] if a_row else "Applicant"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if action == 'accept':
            cursor.execute("UPDATE project_teammates SET status = 'Accepted' WHERE post_id = ? AND student_id = ?", (post_id, applicant_id))
            
            # Send notification to applicant
            notif_id = "notif_" + str(uuid.uuid4())[:8]
            cursor.execute("""
                INSERT INTO notifications (notification_id, user_id, type, title, message, reference_id, sender_id, is_read, created_at)
                VALUES (?, ?, 'join_accepted', ?, ?, ?, ?, 0, ?)
            """, (
                notif_id,
                applicant_id,
                "Join Request Accepted!",
                f"Congratulations! {creator_name} accepted your request to join '{post['idea_title']}'.",
                post_id,
                creator_id,
                now
            ))
            
            # Mark join_request notification as read
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ? AND reference_id = ? AND sender_id = ? AND type = 'join_request'", (creator_id, post_id, applicant_id))
            
            conn.commit()
            conn.close()
            return {"success": True, "message": f"{applicant_name} is now accepted into the project team!"}
        
        elif action == 'reject':
            cursor.execute("DELETE FROM project_teammates WHERE post_id = ? AND student_id = ?", (post_id, applicant_id))
            
            # Send notification to applicant
            notif_id = "notif_" + str(uuid.uuid4())[:8]
            cursor.execute("""
                INSERT INTO notifications (notification_id, user_id, type, title, message, reference_id, sender_id, is_read, created_at)
                VALUES (?, ?, 'join_rejected', ?, ?, ?, ?, 0, ?)
            """, (
                notif_id,
                applicant_id,
                "Join Request Update",
                f"{creator_name} declined your request to join '{post['idea_title']}'.",
                post_id,
                creator_id,
                now
            ))
            
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ? AND reference_id = ? AND sender_id = ? AND type = 'join_request'", (creator_id, post_id, applicant_id))
            
            conn.commit()
            conn.close()
            return {"success": True, "message": "Join request declined."}
            
        conn.close()
        return {"success": False, "message": "Invalid action. Use 'accept' or 'reject'."}

    @staticmethod
    def delete_post(post_id, user_id, is_admin):
        conn = get_db()
        cursor = conn.cursor()
        
        if is_admin:
            cursor.execute("DELETE FROM project_posts WHERE post_id = ?", (post_id,))
        else:
            cursor.execute("DELETE FROM project_posts WHERE post_id = ? AND student_id = ?", (post_id, user_id))
            
        success = cursor.rowcount > 0
        if success:
            cursor.execute("DELETE FROM project_teammates WHERE post_id = ?", (post_id,))
            conn.commit()
            
        conn.close()
        return success
