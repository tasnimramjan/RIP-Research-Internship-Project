import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.availability import AvailabilityModel

class AvailabilityController:
    @staticmethod
    def search(params):
        keywords = params.get('keywords', '')
        dept = params.get('department', '')
        domain = params.get('domain', '')
        status = params.get('status', '')
        
        results = AvailabilityModel.search_availability(
            keywords_str=keywords,
            dept=dept if dept else None,
            domain=domain if domain else None,
            status=status if status else None
        )
        
        return {"success": True, "results": results}

    @staticmethod
    def update_availability(faculty_id, data):
        if not faculty_id:
            return {"success": False, "message": "Faculty ID is required."}
            
        max_cap = data.get('max_capacity')
        curr_students = data.get('current_students')
        slots = data.get('remaining_slots')
        avail_status = data.get('thesis_available')
        designation = data.get('designation')
        domains = data.get('research_domains')
        min_cgpa = data.get('min_cgpa_req')
        
        ok = AvailabilityModel.update_availability_record(
            faculty_id,
            max_capacity=max_cap,
            current_students=curr_students,
            remaining_slots=slots,
            thesis_available=avail_status,
            designation=designation,
            research_domains=domains,
            min_cgpa_req=min_cgpa
        )
        return {"success": ok, "message": "Availability and capacity record updated successfully." if ok else "Failed to update record."}
