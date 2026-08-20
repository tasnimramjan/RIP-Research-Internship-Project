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
