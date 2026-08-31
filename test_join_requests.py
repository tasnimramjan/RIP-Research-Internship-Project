import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))
from controllers.project_controller import ProjectController
from models.project import ProjectModel

class TestJoinRequestsWorkflow(unittest.TestCase):

    def test_01_request_to_join_and_notification(self):
        print("\n--- Testing Request to Join Workflow ---")
        # 1. Student 1 creates project
        create_res = ProjectController.create_post("stu_1", {
            "idea_title": "Quantum ML Research",
            "description": "Exploration of quantum variational circuits for machine learning.",
            "required_skills": "Python, Qiskit, PyTorch"
        })
        self.assertTrue(create_res["success"])
        post_id = create_res["post_id"]
        print("Created project post:", post_id)

        # 2. Student 2 requests to join
        join_res = ProjectController.join_team(post_id, "stu_2")
        self.assertTrue(join_res["success"])
        print("stu_2 join request response:", join_res["message"])

        # 3. Fetch Student 1's join requests menu
        stu1_reqs = ProjectController.get_join_requests("stu_1")
        self.assertTrue(stu1_reqs["success"])
        self.assertGreaterEqual(stu1_reqs["pending_count"], 1)
        incoming_req = next((r for r in stu1_reqs["incoming"] if r["post_id"] == post_id and r["applicant_id"] == "stu_2"), None)
        self.assertIsNotNone(incoming_req)
        self.assertEqual(incoming_req["status"], "Pending")
        print(f"Verified incoming request for stu_1 from {incoming_req['applicant_name']} for {incoming_req['idea_title']}")

        # 4. Fetch Student 2's outgoing requests
        stu2_reqs = ProjectController.get_join_requests("stu_2")
        self.assertTrue(stu2_reqs["success"])
        outgoing_req = next((r for r in stu2_reqs["outgoing"] if r["post_id"] == post_id), None)
        self.assertIsNotNone(outgoing_req)
        self.assertEqual(outgoing_req["status"], "Pending")
        print(f"Verified outgoing request for stu_2 (Status: {outgoing_req['status']})")

        # 5. Student 1 accepts Student 2's request
        accept_res = ProjectController.respond_join({
            "post_id": post_id,
            "applicant_id": "stu_2",
            "creator_id": "stu_1",
            "action": "accept"
        })
        self.assertTrue(accept_res["success"])
        print("Accept join request result:", accept_res["message"])

        # 6. Verify Student 2 is now in accepted teammates
        all_posts = ProjectController.get_all_posts()["posts"]
        target = next((p for p in all_posts if p["post_id"] == post_id), None)
        self.assertIsNotNone(target)
        tm_ids = [t["student_id"] for t in target["teammates"]]
        self.assertIn("stu_2", tm_ids)
        print("Verified stu_2 is accepted in project team members:", tm_ids)

    def test_02_reject_join_request(self):
        print("\n--- Testing Reject Join Request ---")
        # Student 1 creates project
        create_res = ProjectController.create_post("stu_1", {
            "idea_title": "Robotics Vision Project",
            "description": "SLAM and visual odometry algorithms.",
            "required_skills": "C++, OpenCV, ROS"
        })
        post_id = create_res["post_id"]

        # Student 2 requests to join
        ProjectController.join_team(post_id, "stu_2")

        # Student 1 rejects Student 2's request
        reject_res = ProjectController.respond_join({
            "post_id": post_id,
            "applicant_id": "stu_2",
            "creator_id": "stu_1",
            "action": "reject"
        })
        self.assertTrue(reject_res["success"])
        print("Reject join request result:", reject_res["message"])

        # Verify Student 2 is not in teammates
        all_posts = ProjectController.get_all_posts()["posts"]
        target = next((p for p in all_posts if p["post_id"] == post_id), None)
        tm_ids = [t["student_id"] for t in target["teammates"]]
        self.assertNotIn("stu_2", tm_ids)
        print("Verified stu_2 was correctly not added to teammates.")

if __name__ == "__main__":
    unittest.main()
