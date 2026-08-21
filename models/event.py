import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class EventModel:
    @staticmethod
    def get_all_events(category=None):
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY event_date ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create_event(title, category, organizer, event_date, location, description, registration_link=None):
        conn = get_db()
        cursor = conn.cursor()
        event_id = "evt_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO events (event_id, title, category, organizer, event_date, location, description, registration_link, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event_id, title, category, organizer, event_date, location, description, registration_link, now)
        )
        conn.commit()
        conn.close()
        return event_id

    @staticmethod
    def register_user(event_id, user_id):
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute(
                "INSERT INTO event_registrations (event_id, user_id, registered_at) VALUES (?, ?, ?)",
                (event_id, user_id, now)
            )
            conn.commit()
            res = {"success": True, "message": "Registered for event successfully."}
        except Exception:
            res = {"success": False, "message": "Already registered for this event."}
        finally:
            conn.close()
        return res

    @staticmethod
    def get_user_registrations(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, r.registered_at 
            FROM event_registrations r
            JOIN events e ON r.event_id = e.event_id
            WHERE r.user_id = ?
            ORDER BY e.event_date ASC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]