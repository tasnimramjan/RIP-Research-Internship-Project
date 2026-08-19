import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.lab import LabModel

class LabController:
    @staticmethod
    def get_all_labs(search_name=None):
        labs = LabModel.get_all_labs(search_name=search_name)
        return {"success": True, "count": len(labs), "labs": labs}

    @staticmethod
    def get_lab_detail(lab_id):
        lab = LabModel.get_lab_by_id(lab_id)
        if not lab:
            return {"success": False, "message": "Research Lab not found."}
        return {"success": True, "lab": lab}

    @staticmethod
    def post_ra(lab_id, data):
        title = data.get('title')
        desc = data.get('description')
        stipend = data.get('stipend')
        deadline = data.get('deadline')
        
        if not title or not desc:
            return {"success": False, "message": "Title and description are required."}
            
        ra_id = LabModel.post_ra_opportunity(lab_id, title, desc, stipend, deadline)
        return {"success": True, "ra_id": ra_id, "message": "RA Opportunity posted successfully."}
