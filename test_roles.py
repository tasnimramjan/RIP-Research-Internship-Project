import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))
from controllers.project_controller import ProjectController

class TestProjectRolePermissions(unittest.TestCase):

    def test_01_student_can_create_and_join(self):
        print("\n--- Testing Student Permissions ---")
        create_res = ProjectController.create_post("stu_1", {
            "idea_title": "Student Research Project",
            "description": "Student driven project idea.",
            "required_skills": "Python, SQL"
        })
        self.assertTrue(create_res["success"])
        post_id = create_res["post_id"]
        print("Student created post successfully:", post_id)

        join_res = ProjectController.join_team(post_id, "stu_2")
        self.assertTrue(join_res["success"])
        print("Student stu_2 joined post successfully:", join_res["message"])

    def test_02_faculty_cannot_create_or_join(self):
        print("\n--- Testing Faculty Restrictions ---")
        fac_create = ProjectController.create_post("fac_1", {
            "idea_title": "Faculty Project",
            "description": "Trying to create as faculty",
            "required_skills": "Python"
        })
        self.assertFalse(fac_create["success"])
        print("Faculty post creation correctly blocked:", fac_create["message"])

        posts = ProjectController.get_all_posts()["posts"]
        target_post = posts[0]["post_id"]
        fac_join = ProjectController.join_team(target_post, "fac_1")
        self.assertFalse(fac_join["success"])
        print("Faculty join team correctly blocked:", fac_join["message"])

    def test_03_admin_restrictions_and_deletion(self):
        print("\n--- Testing Admin Permissions & Restrictions ---")
        posts = ProjectController.get_all_posts()["posts"]
        target_post = posts[0]["post_id"]

        admin_join = ProjectController.join_team(target_post, "admin_1")
        self.assertFalse(admin_join["success"])
        print("Admin join team correctly blocked:", admin_join["message"])

        del_res = ProjectController.delete_post("admin_1", target_post)
        self.assertTrue(del_res["success"])
        print("Admin delete post successful:", del_res["message"])

if __name__ == "__main__":
    unittest.main()
