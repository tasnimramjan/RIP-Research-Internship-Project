import unittest
import sys
import os

sys.path.append(os.path.dirname(__file__))
from db import get_db, init_db
from models.user import UserModel
from models.lab import LabModel
from controllers.lab_controller import LabController
from controllers.admin_controller import AdminController

class TestLabDelete(unittest.TestCase):
    def setUp(self):
        init_db()
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM research_labs WHERE lab_id IN ('lab_test_fac', 'lab_test_adm')")
        cursor.execute("DELETE FROM users WHERE user_id IN ('fac_lab_owner', 'admin_lab_user')")
        
        pw_hash = UserModel.hash_password("password123")
        cursor.execute("INSERT INTO users (user_id, name, email, password_hash, department, role) VALUES ('fac_lab_owner', 'Dr. Lab Owner', 'fac_owner@univ.edu', ?, 'CSE', 'Faculty')", (pw_hash,))
        cursor.execute("INSERT INTO users (user_id, name, email, password_hash, department, role) VALUES ('admin_lab_user', 'System Admin', 'admin_lab@univ.edu', ?, 'CSE', 'Admin')", (pw_hash,))

        cursor.execute("INSERT INTO research_labs (lab_id, lab_name, focus_area, facilities, faculty_id) VALUES ('lab_test_fac', 'Faculty AI Lab', 'Machine Learning', '[\"GPUs\"]', 'fac_lab_owner')")
        cursor.execute("INSERT INTO research_labs (lab_id, lab_name, focus_area, facilities, faculty_id) VALUES ('lab_test_adm', 'Admin Robotics Lab', 'Robotics', '[\"Sensors\"]', 'fac_lab_owner')")
        
        conn.commit()
        conn.close()

    def test_faculty_delete_own_lab(self):
        res = LabController.delete_lab('lab_test_fac', 'fac_lab_owner')
        self.assertTrue(res['success'])
        lab = LabModel.get_lab_by_id('lab_test_fac')
        self.assertIsNone(lab)

    def test_admin_delete_any_lab(self):
        res = AdminController.delete_lab('lab_test_adm')
        self.assertTrue(res['success'])
        lab = LabModel.get_lab_by_id('lab_test_adm')
        self.assertIsNone(lab)

if __name__ == '__main__':
    unittest.main()
