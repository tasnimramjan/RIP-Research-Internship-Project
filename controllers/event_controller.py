import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.event import EventModel

class EventController:
    @staticmethod
    def get_events(category=None):
        events = EventModel.get_all_events(category=category)
        return {"success": True, "count": len(events), "events": events}

    @staticmethod
    def create_event(data):
        title = data.get('title')
        category = data.get('category', 'Seminar')
        organizer = data.get('organizer')
        event_date = data.get('event_date')
        location = data.get('location', 'Main Campus')
        desc = data.get('description', '')
        link = data.get('registration_link')

        if not title or not organizer or not event_date:
            return {"success": False, "message": "Title, organizer, and date are required."}

        evt_id = EventModel.create_event(title, category, organizer, event_date, location, desc, link)
        return {"success": True, "event_id": evt_id, "message": "Research event published successfully."}

    @staticmethod
    def register_event(event_id, user_id):
        from db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {"success": False, "message": "User not found."}
        if row["role"] != "Student":
            return {"success": False, "message": "Only students can register for events."}

        return EventModel.register_user(event_id, user_id)

    @staticmethod
    def my_registrations(user_id):
        regs = EventModel.get_user_registrations(user_id)
        return {"success": True, "registrations": regs}