import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.supervisor import SupervisorModel

class SupervisorController:
    @staticmethod
    def handle_search(params):
        department = params.get('department')
        keyword = params.get('keyword')
        cgpa = params.get('cgpa')
        avail_only = params.get('availability_only') in ['true', '1', True]
        
        supervisors = SupervisorModel.search_supervisors(
            department=department,
            keyword=keyword,
            cgpa=float(cgpa) if cgpa else None,
            availability_only=avail_only
        )
        return {"success": True, "count": len(supervisors), "supervisors": supervisors}

    @staticmethod
    def handle_update_availability(faculty_id, data):
        slots = data.get('remaining_slots')
        avail = data.get('thesis_available')
        min_cgpa = data.get('min_cgpa_req')
        
        ok = SupervisorModel.update_availability(
            faculty_id,
            slots=slots,
            thesis_available=avail,
            min_cgpa_req=min_cgpa
        )
        if ok:
            return {"success": True, "message": "Supervision availability updated successfully."}
        return {"success": False, "message": "Failed to update availability."}
