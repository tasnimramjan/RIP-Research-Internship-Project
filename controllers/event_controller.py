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
        return EventModel.register_user(event_id, user_id)

    @staticmethod
    def my_registrations(user_id):
        regs = EventModel.get_user_registrations(user_id)
        return {"success": True, "registrations": regs}