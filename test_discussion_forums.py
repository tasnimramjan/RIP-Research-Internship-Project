import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(__file__))
from controllers.forum_controller import ForumController
from models.forum import DiscussionModel
from db import get_db

class TestDiscussionForums(unittest.TestCase):

    def test_01_spaces_access_control_by_activity(self):
        print("\n--- Testing Space Access Permissions by Activity & Role ---")
        
        # 1. Admin has access to all 5 spaces
        admin_acc = DiscussionModel.get_user_spaces_access("admin_1")
        self.assertTrue(all(admin_acc.values()))
        print("Admin access verified for all spaces:", admin_acc)

        # 2. Student with thesis activity
        stu_acc = DiscussionModel.get_user_spaces_access("stu_1")
        print("Student (stu_1) access verified:", stu_acc)
        self.assertTrue(stu_acc["General Academic Discussions"])

        # 3. Create inactive student and verify locked access
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, email, password_hash, name, role, department) VALUES ('stu_inactive', 'inactive@test.com', 'pass', 'Inactive User', 'Student', 'CSE')")
        cursor.execute("INSERT OR REPLACE INTO students (student_id, cgpa, research_interests) VALUES ('stu_inactive', 3.5, 'AI')")
        conn.commit()
        conn.close()

        inactive_acc = DiscussionModel.get_user_spaces_access("stu_inactive")
        self.assertTrue(inactive_acc["General Academic Discussions"])
        self.assertFalse(inactive_acc["Thesis"]) # Not in any thesis group
        self.assertFalse(inactive_acc["Projects"]) # No project posts
        print("Inactive student access correctly restricted to General only:", inactive_acc)

        # Inactive student trying to post in Thesis should be blocked
        blocked_post = ForumController.create_thread("stu_inactive", {
            "title": "Unauthorized Thesis Post",
            "category": "Thesis",
            "content": "Trying to post without thesis activity."
        })
        self.assertFalse(blocked_post["success"])
        self.assertIn("Access to Thesis is restricted. Students and faculty can see their respective discussion space.", blocked_post["message"])
        print("Blocked unauthorized thread creation with correct message:", blocked_post["message"])

    def test_01b_faculty_space_access_control(self):
        print("\n--- Testing Faculty Space Access (Not Automatically Granted) ---")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, email, password_hash, name, role, department) VALUES ('fac_test', 'fac_test@univ.edu', 'pass', 'Dr. Test', 'Faculty', 'CSE')")
        cursor.execute("INSERT OR REPLACE INTO faculty (faculty_id, designation, h_index, research_domains, remaining_slots, thesis_available) VALUES ('fac_test', 'Assistant Professor', 5, 'AI', 0, 0)")
        conn.commit()
        conn.close()

        # Faculty without thesis availability or lab projects or internship postings
        fac_acc = DiscussionModel.get_user_spaces_access("fac_test")
        self.assertTrue(fac_acc["General Academic Discussions"])
        self.assertFalse(fac_acc["Thesis"])
        self.assertFalse(fac_acc["Projects"])
        self.assertFalse(fac_acc["Internships"])
        print("Faculty without active involvement correctly restricted:", fac_acc)

        # Blocked when attempting to post in Projects
        blocked_fac_post = ForumController.create_thread("fac_test", {
            "title": "Faculty Project Post",
            "category": "Projects",
            "content": "Project discussion without lab projects."
        })
        self.assertFalse(blocked_fac_post["success"])
        self.assertIn("Access to Projects is restricted. Students and faculty can see their respective discussion space.", blocked_fac_post["message"])
        print("Blocked faculty unauthorized post correctly:", blocked_fac_post["message"])

    def test_02_create_and_get_threads(self):
        print("\n--- Testing Thread Creation & Fetching by Space ---")
        # Ensure stu_1 has access to all spaces by adding activity
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO thesis_groups (group_id, group_name, topic, description, creator_id, created_at) VALUES ('tg_test', 'Test Group', 'AI', 'Desc', 'stu_1', '2026-09-01 00:00:00')")
        cursor.execute("INSERT OR REPLACE INTO project_posts (post_id, student_id, idea_title, description, required_skills, created_at) VALUES ('pp_test', 'stu_1', 'Test Proj', 'Desc', 'Python', '2026-09-01 00:00:00')")
        cursor.execute("INSERT OR REPLACE INTO internship_applications (application_id, opportunity_id, student_id, status, applied_at) VALUES ('app_test', 'opp_1', 'stu_1', 'Pending', '2026-09-01 00:00:00')")
        conn.commit()
        conn.close()

        spaces = ['Thesis', 'Projects', 'Internships', 'Defense Preparation', 'General Academic Discussions']
        for space in spaces:
            res = ForumController.create_thread("stu_1", {
                "title": f"Question for {space}",
                "category": space,
                "content": f"Detailed discussion for {space}."
            })
            self.assertTrue(res["success"])
            print(f"Created thread in '{space}': {res['thread_id']}")

        # Fetch all threads
        all_threads = ForumController.get_threads()["threads"]
        self.assertGreaterEqual(len(all_threads), len(spaces))
        
        # Fetch by category
        thesis_threads = ForumController.get_threads("Thesis")["threads"]
        self.assertTrue(all(t["category"] == "Thesis" for t in thesis_threads))
        print("Verified category filtering for 'Thesis': Found", len(thesis_threads), "threads.")

    def test_03_comments_and_reactions(self):
        print("\n--- Testing Comments & Reactions ---")
        t_res = ForumController.create_thread("stu_1", {
            "title": "Defense Presentation Tips",
            "category": "Defense Preparation",
            "content": "What are common questions asked during project defense?"
        })
        thread_id = t_res["thread_id"]

        # Add comment
        c_res = ForumController.add_comment("stu_1", {
            "thread_id": thread_id,
            "content": "Make sure to explain your methodology clearly."
        })
        self.assertTrue(c_res["success"])
        print("Added comment:", c_res["message"])

        # Add reaction
        r_res = ForumController.add_reaction("stu_1", {
            "thread_id": thread_id,
            "reaction_type": "like"
        })
        self.assertTrue(r_res["success"])
        self.assertEqual(r_res["action"], "added")

        # Toggle reaction (Unlike)
        r_toggle = ForumController.add_reaction("stu_1", {
            "thread_id": thread_id,
            "reaction_type": "like"
        })
        self.assertTrue(r_toggle["success"])
        self.assertEqual(r_toggle["action"], "removed")
        print("Reaction toggle verified successfully.")

    def test_04_specific_date_time_thread_reminders(self):
        print("\n--- Testing Specific Date & Time Thread Reminders ---")
        t_res = ForumController.create_thread("stu_1", {
            "title": "Thesis Final Draft Due",
            "category": "Thesis",
            "content": "Submission reminder."
        })
        thread_id = t_res["thread_id"]

        # Specific date and time (e.g. Date: 25/08/2026, Time: 10:30 PM -> 2026-08-25 22:30:00)
        specific_datetime = "2026-08-25 22:30:00"
        rem_res = ForumController.set_reminder("stu_1", {
            "thread_id": thread_id,
            "remind_at": specific_datetime,
            "note": "Follow up on thesis draft before defense"
        })
        self.assertTrue(rem_res["success"])
        print(f"Specific date/time reminder scheduled: {rem_res['message']}")

        # Set due reminder for right now and verify polling trigger
        due_datetime = (datetime.now() - timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")
        ForumController.set_reminder("stu_1", {
            "thread_id": thread_id,
            "remind_at": due_datetime,
            "note": "Due reminder test"
        })
        due = ForumController.check_reminders("stu_1")["reminders"]
        self.assertTrue(any(r["thread_id"] == thread_id for r in due))
        print("Verified real-time due reminder trigger.")

    def test_05_thread_deletion(self):
        print("\n--- Testing Thread Deletion ---")
        t_res = ForumController.create_thread("stu_1", {
            "title": "Thread to Delete",
            "category": "General Academic Discussions",
            "content": "To be deleted."
        })
        thread_id = t_res["thread_id"]

        del_res = ForumController.delete_thread("stu_1", {"thread_id": thread_id})
        self.assertTrue(del_res["success"])
        print("Deleted thread successfully.")

if __name__ == "__main__":
    unittest.main()
