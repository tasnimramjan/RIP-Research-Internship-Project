import uuid
from datetime import datetime
import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

ALL_SPACES = [
    "Thesis",
    "Projects",
    "Internships",
    "Defense Preparation",
    "General Academic Discussions"
]

class DiscussionModel:
    @staticmethod
    def get_accessible_spaces(user_id):
        """
        Determines which discussion spaces the student/faculty/admin has access to based on their activity/role.
        Access Rule:
        - Admin: full access to all 5 spaces.
        - Faculty:
          * General Academic Discussions: Accessible to all.
          * Thesis: Accessible if thesis_available = 1 or supervising thesis groups.
          * Projects: Accessible if directing a lab in research_labs or supervising lab projects.
          * Internships: Accessible for faculty in departments offering internships / academic involvement.
          * Defense Preparation: Accessible if thesis supervisor / senior faculty (Prof/Assoc/Asst Prof).
        - Student:
          * General Academic Discussions: Accessible to all.
          * Thesis: Accessible if student created or joined a thesis group (thesis_groups / thesis_group_members).
          * Projects: Accessible if student created project post or joined project team (project_posts / project_teammates).
          * Internships: Accessible if student has applied for internship (internship_applications).
          * Defense Preparation: Accessible if student is thesis group member / candidate at defense phase.
        """
        if not user_id:
            return {
                "accessible_spaces": ["General Academic Discussions"],
                "all_spaces": ALL_SPACES,
                "space_status": {s: (s == "General Academic Discussions") for s in ALL_SPACES},
                "space_reasons": {
                    "General Academic Discussions": "Open to all campus members.",
                    "Thesis": "Please log in to check Thesis participation.",
                    "Projects": "Please log in to check Project participation.",
                    "Internships": "Please log in to check Internship participation.",
                    "Defense Preparation": "Please log in to check Defense eligibility."
                },
                "is_admin": False
            }

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return {
                "accessible_spaces": ["General Academic Discussions"],
                "all_spaces": ALL_SPACES,
                "space_status": {s: (s == "General Academic Discussions") for s in ALL_SPACES},
                "space_reasons": {s: "User record not found." for s in ALL_SPACES},
                "is_admin": False
            }

        role = user['role']
        is_admin = (role == 'Admin')

        accessible = []
        space_status = {}
        space_reasons = {}

        if is_admin:
            accessible = list(ALL_SPACES)
            for s in ALL_SPACES:
                space_status[s] = True
                space_reasons[s] = "Full Administrator access for monitoring, moderation, and management."
            conn.close()
            return {
                "accessible_spaces": accessible,
                "all_spaces": ALL_SPACES,
                "space_status": space_status,
                "space_reasons": space_reasons,
                "is_admin": True,
                "user_role": role
            }

        if role == 'Faculty':
            # 1. General Academic Discussions
            space_status["General Academic Discussions"] = True
            space_reasons["General Academic Discussions"] = "Open to all faculty members."
            accessible.append("General Academic Discussions")

            # Check faculty details
            cursor.execute("SELECT * FROM faculty WHERE faculty_id = ?", (user_id,))
            fac = cursor.fetchone()

            # 2. Thesis
            has_thesis = bool(fac and (fac['thesis_available'] == 1 or fac['current_students'] > 0))
            if not has_thesis:
                # check directed thesis groups
                cursor.execute("SELECT COUNT(*) FROM thesis_groups WHERE creator_id = ?", (user_id,))
                has_thesis = (cursor.fetchone()[0] > 0)
            
            space_status["Thesis"] = has_thesis
            space_reasons["Thesis"] = "Active thesis supervisor availability confirmed." if has_thesis else "Unlocked when thesis supervision slots are active."
            if has_thesis:
                accessible.append("Thesis")

            # 3. Projects
            cursor.execute("SELECT COUNT(*) FROM research_labs WHERE faculty_id = ?", (user_id,))
            has_labs = (cursor.fetchone()[0] > 0)
            space_status["Projects"] = has_labs
            space_reasons["Projects"] = "Directing research labs / projects." if has_labs else "Unlocked when directing research labs or student capstone projects."
            if has_labs:
                accessible.append("Projects")

            # 4. Internships
            # Faculty from academic depts with active internships
            space_status["Internships"] = True
            space_reasons["Internships"] = f"Departmental academic coordinator for {user['department']} internships."
            accessible.append("Internships")

            # 5. Defense Preparation
            is_senior = bool(fac and (fac['designation'] in ('Professor', 'Associate Professor', 'Assistant Professor') or fac['thesis_available'] == 1))
            space_status["Defense Preparation"] = is_senior
            space_reasons["Defense Preparation"] = "Faculty evaluation committee & defense board member." if is_senior else "Restricted to faculty defense committee members."
            if is_senior:
                accessible.append("Defense Preparation")

        elif role == 'Student':
            # 1. General Academic Discussions
            space_status["General Academic Discussions"] = True
            space_reasons["General Academic Discussions"] = "Open to all students."
            accessible.append("General Academic Discussions")

            # 2. Thesis (Member or Creator of a Thesis Group)
            cursor.execute("""
                SELECT (
                    (SELECT COUNT(*) FROM thesis_groups WHERE creator_id = ?) +
                    (SELECT COUNT(*) FROM thesis_group_members WHERE student_id = ?)
                )
            """, (user_id, user_id))
            in_thesis_group = (cursor.fetchone()[0] > 0)
            space_status["Thesis"] = in_thesis_group
            space_reasons["Thesis"] = "Active member in Thesis Study Group." if in_thesis_group else "Locked: Join or create a Thesis Study Circle in Thesis Group Finder to access."
            if in_thesis_group:
                accessible.append("Thesis")

            # 3. Projects (Created project post or joined project teammates)
            cursor.execute("""
                SELECT (
                    (SELECT COUNT(*) FROM project_posts WHERE student_id = ?) +
                    (SELECT COUNT(*) FROM project_teammates WHERE student_id = ?)
                )
            """, (user_id, user_id))
            in_projects = (cursor.fetchone()[0] > 0)
            space_status["Projects"] = in_projects
            space_reasons["Projects"] = "Active participant in Project Teammate Finder." if in_projects else "Locked: Post a project idea or join a project team to access."
            if in_projects:
                accessible.append("Projects")

            # 4. Internships (Applied for internships)
            cursor.execute("SELECT COUNT(*) FROM internship_applications WHERE student_id = ?", (user_id,))
            has_internship_app = (cursor.fetchone()[0] > 0)
            space_status["Internships"] = has_internship_app
            space_reasons["Internships"] = "Active applicant in Internship Portal." if has_internship_app else "Locked: Apply for an internship opportunity in the Internship Portal to access."
            if has_internship_app:
                accessible.append("Internships")

            # 5. Defense Preparation (Thesis student at defense stage)
            # Student in thesis group
            space_status["Defense Preparation"] = in_thesis_group
            space_reasons["Defense Preparation"] = "Thesis candidate eligible for defense preparation." if in_thesis_group else "Locked: Requires active thesis study group membership."
            if in_thesis_group:
                accessible.append("Defense Preparation")

        conn.close()
        return {
            "accessible_spaces": accessible,
            "all_spaces": ALL_SPACES,
            "space_status": space_status,
            "space_reasons": space_reasons,
            "is_admin": is_admin,
            "user_role": role
        }

    @staticmethod
    def get_threads(category=None, user_id=None):
        conn = get_db()
        cursor = conn.cursor()

        access_info = DiscussionModel.get_accessible_spaces(user_id) if user_id else None
        accessible_spaces = access_info["accessible_spaces"] if access_info else ALL_SPACES
        is_admin = access_info["is_admin"] if access_info else False

        # If user explicitly requested a category, verify access (unless admin)
        if category and category != "All":
            if not is_admin and user_id and category not in accessible_spaces:
                conn.close()
                return []

        query = """
        SELECT t.*, u.name as author_name, u.role as author_role, u.department
        FROM discussion_threads t
        JOIN users u ON t.user_id = u.user_id
        """
        params = []
        if category and category != "All":
            query += " WHERE t.category = ?"
            params.append(category)
        elif not is_admin and user_id:
            # Filter to accessible spaces for this user
            placeholders = ','.join('?' for _ in accessible_spaces)
            query += f" WHERE t.category IN ({placeholders})"
            params.extend(accessible_spaces)

        query += " ORDER BY t.created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        threads = []
        for r in rows:
            t = dict(r)
            thread_id = t['thread_id']

            # Comments with author info and reaction counts
            cursor.execute("""
            SELECT c.*, u.name as author_name, u.role as author_role, u.department
            FROM forum_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.thread_id = ?
            ORDER BY c.created_at ASC
            """, (thread_id,))
            comments_raw = cursor.fetchall()
            
            comments = []
            for c in comments_raw:
                c_dict = dict(c)
                cid = c_dict['comment_id']
                # Comment reactions
                cursor.execute("""
                SELECT reaction_type, COUNT(*) as count
                FROM forum_reactions
                WHERE comment_id = ?
                GROUP BY reaction_type
                """, (cid,))
                c_dict['reactions'] = {r_row['reaction_type']: r_row['count'] for r_row in cursor.fetchall()}
                
                # Check if current user reacted to comment
                c_dict['user_reacted'] = False
                if user_id:
                    cursor.execute("SELECT reaction_type FROM forum_reactions WHERE comment_id = ? AND user_id = ?", (cid, user_id))
                    user_c_react = cursor.fetchone()
                    if user_c_react:
                        c_dict['user_reacted'] = True
                        c_dict['user_reaction_type'] = user_c_react['reaction_type']

                c_dict['can_delete'] = bool(user_id and (user_id == c_dict['user_id'] or is_admin))
                comments.append(c_dict)

            t['comments'] = comments

            # Thread reaction counts
            cursor.execute("""
            SELECT reaction_type, COUNT(*) as count
            FROM forum_reactions
            WHERE thread_id = ? AND comment_id IS NULL
            GROUP BY reaction_type
            """, (thread_id,))
            t['reactions'] = {r_row['reaction_type']: r_row['count'] for r_row in cursor.fetchall()}

            # Check if current user reacted to this thread
            t['user_reacted'] = False
            t['user_reaction_type'] = None
            if user_id:
                cursor.execute("SELECT reaction_type FROM forum_reactions WHERE thread_id = ? AND comment_id IS NULL AND user_id = ?", (thread_id, user_id))
                u_react = cursor.fetchone()
                if u_react:
                    t['user_reacted'] = True
                    t['user_reaction_type'] = u_react['reaction_type']

            # Check if user has an active reminder on this thread
            t['user_reminder'] = None
            if user_id:
                cursor.execute("""
                SELECT reminder_id, remind_at, note, is_triggered 
                FROM thread_reminders 
                WHERE thread_id = ? AND user_id = ? AND is_triggered = 0
                ORDER BY remind_at ASC LIMIT 1
                """, (thread_id, user_id))
                rem_row = cursor.fetchone()
                if rem_row:
                    t['user_reminder'] = dict(rem_row)

            t['can_delete'] = bool(user_id and (user_id == t['user_id'] or is_admin))
            threads.append(t)

        conn.close()
        return threads

    @staticmethod
    def create_thread(user_id, title, category, content):
        if not user_id or not title or not content:
            return {"success": False, "message": "Missing required fields."}

        access_info = DiscussionModel.get_accessible_spaces(user_id)
        if category not in access_info["accessible_spaces"] and not access_info["is_admin"]:
            reason = access_info["space_reasons"].get(category, "You do not have access to this discussion space.")
            return {"success": False, "message": f"Access Restricted: {reason}"}

        conn = get_db()
        cursor = conn.cursor()
        thread_id = "th_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO discussion_threads (thread_id, user_id, title, category, content, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (thread_id, user_id, title, category, content, now)
        )
        conn.commit()
        conn.close()
        return {"success": True, "thread_id": thread_id, "message": f"Thread created in {category}."}

    @staticmethod
    def add_comment(thread_id, user_id, content):
        if not thread_id or not user_id or not content:
            return {"success": False, "message": "Thread ID, user ID, and content are required."}

        conn = get_db()
        cursor = conn.cursor()

        # Check thread and verify category access
        cursor.execute("SELECT category FROM discussion_threads WHERE thread_id = ?", (thread_id,))
        th = cursor.fetchone()
        if not th:
            conn.close()
            return {"success": False, "message": "Discussion thread not found."}

        category = th['category']
        access_info = DiscussionModel.get_accessible_spaces(user_id)
        if category not in access_info["accessible_spaces"] and not access_info["is_admin"]:
            conn.close()
            return {"success": False, "message": f"Access Restricted: You cannot comment in the {category} space."}

        comment_id = "c_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO forum_comments (comment_id, thread_id, user_id, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (comment_id, thread_id, user_id, content, now)
        )
        conn.commit()
        conn.close()
        return {"success": True, "comment_id": comment_id, "message": "Comment posted successfully."}

    @staticmethod
    def delete_comment(comment_id, user_id):
        if not comment_id or not user_id:
            return {"success": False, "message": "Comment ID and User ID are required."}

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        is_admin = bool(user_row and user_row['role'] == 'Admin')

        if is_admin:
            cursor.execute("DELETE FROM forum_comments WHERE comment_id = ?", (comment_id,))
        else:
            cursor.execute("DELETE FROM forum_comments WHERE comment_id = ? AND user_id = ?", (comment_id, user_id))

        deleted = (cursor.rowcount > 0)
        if deleted:
            cursor.execute("DELETE FROM forum_reactions WHERE comment_id = ?", (comment_id,))
            conn.commit()

        conn.close()
        return {"success": deleted, "message": "Comment deleted." if deleted else "Unauthorized or comment not found."}

    @staticmethod
    def add_reaction(user_id, thread_id=None, comment_id=None, reaction_type="like"):
        if not user_id or (not thread_id and not comment_id):
            return {"success": False, "message": "Invalid reaction parameters."}

        conn = get_db()
        cursor = conn.cursor()

        # Check access to the thread
        target_thread_id = thread_id
        if not target_thread_id and comment_id:
            cursor.execute("SELECT thread_id FROM forum_comments WHERE comment_id = ?", (comment_id,))
            c_row = cursor.fetchone()
            if c_row:
                target_thread_id = c_row['thread_id']

        if target_thread_id:
            cursor.execute("SELECT category FROM discussion_threads WHERE thread_id = ?", (target_thread_id,))
            t_row = cursor.fetchone()
            if t_row:
                category = t_row['category']
                access_info = DiscussionModel.get_accessible_spaces(user_id)
                if category not in access_info["accessible_spaces"] and not access_info["is_admin"]:
                    conn.close()
                    return {"success": False, "message": "Access restricted in this space."}

        # Check if already reacted
        if comment_id:
            cursor.execute("SELECT * FROM forum_reactions WHERE comment_id = ? AND user_id = ? AND reaction_type = ?", (comment_id, user_id, reaction_type))
        else:
            cursor.execute("SELECT * FROM forum_reactions WHERE thread_id = ? AND comment_id IS NULL AND user_id = ? AND reaction_type = ?", (thread_id, user_id, reaction_type))

        existing = cursor.fetchone()

        if existing:
            # User clicked again -> REMOVE own reaction
            if comment_id:
                cursor.execute("DELETE FROM forum_reactions WHERE comment_id = ? AND user_id = ? AND reaction_type = ?", (comment_id, user_id, reaction_type))
            else:
                cursor.execute("DELETE FROM forum_reactions WHERE thread_id = ? AND comment_id IS NULL AND user_id = ? AND reaction_type = ?", (thread_id, user_id, reaction_type))
            action = "removed"
        else:
            # User reacted -> ADD reaction
            cursor.execute(
                "INSERT INTO forum_reactions (thread_id, comment_id, user_id, reaction_type) VALUES (?, ?, ?, ?)",
                (thread_id, comment_id, user_id, reaction_type)
            )
            action = "added"

        conn.commit()

        # Fetch updated count
        if comment_id:
            cursor.execute("SELECT COUNT(*) FROM forum_reactions WHERE comment_id = ? AND reaction_type = ?", (comment_id, reaction_type))
        else:
            cursor.execute("SELECT COUNT(*) FROM forum_reactions WHERE thread_id = ? AND comment_id IS NULL AND reaction_type = ?", (thread_id, reaction_type))

        count = cursor.fetchone()[0]
        conn.close()

        return {
            "success": True,
            "action": action,
            "reaction_type": reaction_type,
            "count": count,
            "message": f"Reaction {action}."
        }

    @staticmethod
    def moderate_reactions(user_id, thread_id=None, comment_id=None):
        """Admin reaction moderation."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        u = cursor.fetchone()
        if not u or u['role'] != 'Admin':
            conn.close()
            return {"success": False, "message": "Admin authorization required."}

        if comment_id:
            cursor.execute("DELETE FROM forum_reactions WHERE comment_id = ?", (comment_id,))
        elif thread_id:
            cursor.execute("DELETE FROM forum_reactions WHERE thread_id = ?", (thread_id,))

        conn.commit()
        conn.close()
        return {"success": True, "message": "Reactions cleared by Administrator."}

    @staticmethod
    def delete_thread(thread_id, user_id):
        if not thread_id or not user_id:
            return {"success": False, "message": "Thread ID and User ID are required."}

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        is_admin = bool(user_row and user_row['role'] == 'Admin')

        if is_admin:
            cursor.execute("DELETE FROM discussion_threads WHERE thread_id = ?", (thread_id,))
        else:
            cursor.execute("DELETE FROM discussion_threads WHERE thread_id = ? AND user_id = ?", (thread_id, user_id))

        deleted = (cursor.rowcount > 0)
        if deleted:
            cursor.execute("DELETE FROM forum_comments WHERE thread_id = ?", (thread_id,))
            cursor.execute("DELETE FROM forum_reactions WHERE thread_id = ?", (thread_id,))
            cursor.execute("DELETE FROM thread_reminders WHERE thread_id = ?", (thread_id,))
            conn.commit()

        conn.close()
        return {"success": deleted, "message": "Discussion thread deleted." if deleted else "Unauthorized or thread not found."}

    @staticmethod
    def set_reminder(thread_id, user_id, remind_at, note=None):
        if not thread_id or not user_id or not remind_at:
            return {"success": False, "message": "Thread ID, User ID, and Reminder Date/Time are required."}

        conn = get_db()
        cursor = conn.cursor()

        # Check access to the thread
        cursor.execute("SELECT title, category FROM discussion_threads WHERE thread_id = ?", (thread_id,))
        th = cursor.fetchone()
        if not th:
            conn.close()
            return {"success": False, "message": "Thread not found."}

        access_info = DiscussionModel.get_accessible_spaces(user_id)
        if th['category'] not in access_info['accessible_spaces'] and not access_info['is_admin']:
            conn.close()
            return {"success": False, "message": "Access restricted: You cannot set reminders for threads in this space."}

        reminder_id = "rem_" + str(uuid.uuid4())[:6]
        
        # Replace existing active reminder for this user and thread if any
        cursor.execute("DELETE FROM thread_reminders WHERE thread_id = ? AND user_id = ?", (thread_id, user_id))
        cursor.execute(
            "INSERT INTO thread_reminders (reminder_id, thread_id, user_id, remind_at, note, is_triggered) VALUES (?, ?, ?, ?, ?, 0)",
            (reminder_id, thread_id, user_id, remind_at, note or f"Reminder for discussion: {th['title']}")
        )
        conn.commit()
        conn.close()

        return {
            "success": True,
            "reminder_id": reminder_id,
            "thread_id": thread_id,
            "thread_title": th['title'],
            "category": th['category'],
            "remind_at": remind_at,
            "note": note,
            "message": f"Thread reminder scheduled for {remind_at}!"
        }

    @staticmethod
    def get_due_reminders(user_id):
        if not user_id:
            return []

        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            SELECT r.*, t.title as thread_title, t.category 
            FROM thread_reminders r
            JOIN discussion_threads t ON r.thread_id = t.thread_id
            WHERE r.user_id = ? AND r.is_triggered = 0 AND r.remind_at <= ?
            ORDER BY r.remind_at ASC
        """, (user_id, now))
        reminders = [dict(r) for r in cursor.fetchall()]

        if reminders:
            ids = [r['reminder_id'] for r in reminders]
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"UPDATE thread_reminders SET is_triggered = 1 WHERE reminder_id IN ({placeholders})", ids)
            conn.commit()

        conn.close()
        return reminders

    @staticmethod
    def get_user_reminders(user_id):
        if not user_id:
            return []
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, t.title as thread_title, t.category
            FROM thread_reminders r
            JOIN discussion_threads t ON r.thread_id = t.thread_id
            WHERE r.user_id = ?
            ORDER BY r.remind_at DESC
        """, (user_id,))
        reminders = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return reminders

    @staticmethod
    def get_all_reminders_admin(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        u = cursor.fetchone()
        if not u or u['role'] != 'Admin':
            conn.close()
            return {"success": False, "message": "Admin authorization required."}

        cursor.execute("""
            SELECT r.*, t.title as thread_title, t.category, u.name as user_name, u.email as user_email
            FROM thread_reminders r
            JOIN discussion_threads t ON r.thread_id = t.thread_id
            JOIN users u ON r.user_id = u.user_id
            ORDER BY r.remind_at DESC
        """)
        reminders = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return {"success": True, "reminders": reminders}

    @staticmethod
    def delete_reminder(reminder_id, user_id):
        if not reminder_id or not user_id:
            return {"success": False, "message": "Reminder ID and User ID are required."}

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        is_admin = bool(user_row and user_row['role'] == 'Admin')

        if is_admin:
            cursor.execute("DELETE FROM thread_reminders WHERE reminder_id = ?", (reminder_id,))
        else:
            cursor.execute("DELETE FROM thread_reminders WHERE reminder_id = ? AND user_id = ?", (reminder_id, user_id))

        deleted = (cursor.rowcount > 0)
        conn.commit()
        conn.close()
        return {"success": deleted, "message": "Reminder dismissed." if deleted else "Unauthorized or reminder not found."}

    @staticmethod
    def get_admin_analytics(user_id=None):
        conn = get_db()
        cursor = conn.cursor()

        if user_id:
            cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
            u = cursor.fetchone()
            if not u or u['role'] != 'Admin':
                conn.close()
                return {"success": False, "message": "Admin authorization required."}

        cursor.execute("SELECT COUNT(*) FROM discussion_threads")
        total_threads = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM forum_comments")
        total_comments = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM forum_reactions")
        total_reactions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM thread_reminders WHERE is_triggered = 0")
        active_reminders = cursor.fetchone()[0]

        # By space
        space_counts = {}
        for s in ALL_SPACES:
            cursor.execute("SELECT COUNT(*) FROM discussion_threads WHERE category = ?", (s,))
            space_counts[s] = cursor.fetchone()[0]

        # Recent activity
        cursor.execute("""
            SELECT t.thread_id, t.title, t.category, t.created_at, u.name as author_name, u.role as author_role
            FROM discussion_threads t
            JOIN users u ON t.user_id = u.user_id
            ORDER BY t.created_at DESC LIMIT 5
        """)
        recent_threads = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return {
            "success": True,
            "stats": {
                "total_threads": total_threads,
                "total_comments": total_comments,
                "total_reactions": total_reactions,
                "active_reminders": active_reminders,
                "spaces": space_counts
            },
            "recent_threads": recent_threads
        }
