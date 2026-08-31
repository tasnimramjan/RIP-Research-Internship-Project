import os
import sys
import unittest
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from models.forum import DiscussionModel, ALL_SPACES
from controllers.forum_controller import ForumController

class TestDiscussionForums(unittest.TestCase):

    def test_01_access_control(self):
        print("\n--- Testing Access Control ---")
        # Admin access: All 5 spaces
        admin_acc = DiscussionModel.get_accessible_spaces("admin_1")
        self.assertTrue(admin_acc["is_admin"])
        self.assertEqual(len(admin_acc["accessible_spaces"]), 5)
        print("Admin access verified:", admin_acc["accessible_spaces"])

        # Student stu_1 (creator of thesis group grp_1 and in project posts and internship apps)
        stu1_acc = DiscussionModel.get_accessible_spaces("stu_1")
        self.assertIn("General Academic Discussions", stu1_acc["accessible_spaces"])
        self.assertIn("Thesis", stu1_acc["accessible_spaces"])
        self.assertIn("Projects", stu1_acc["accessible_spaces"])
        self.assertIn("Internships", stu1_acc["accessible_spaces"])
        print("Student stu_1 access verified:", stu1_acc["accessible_spaces"])

        # Faculty fac_1
        fac1_acc = DiscussionModel.get_accessible_spaces("fac_1")
        self.assertIn("General Academic Discussions", fac1_acc["accessible_spaces"])
        print("Faculty fac_1 access verified:", fac1_acc["accessible_spaces"])

    def test_02_get_threads_and_space_filtering(self):
        print("\n--- Testing Thread Fetching & Space Filtering ---")
        threads_all = DiscussionModel.get_threads(category=None, user_id="admin_1")
        self.assertGreater(len(threads_all), 0)
        print(f"Total seeded threads fetched: {len(threads_all)}")

        # Fetch Thesis space
        thesis_threads = DiscussionModel.get_threads(category="Thesis", user_id="stu_1")
        for t in thesis_threads:
            self.assertEqual(t["category"], "Thesis")
            self.assertIn("comments", t)
            self.assertIn("reactions", t)
        print(f"Thesis threads count: {len(thesis_threads)}")

    def test_03_create_thread_and_permissions(self):
        print("\n--- Testing Thread Creation & Permissions ---")
        # Allowed creation in General Academic Discussions
        res = DiscussionModel.create_thread(
            user_id="stu_1",
            title="Test Thread Title",
            category="General Academic Discussions",
            content="This is a test discussion body."
        )
        self.assertTrue(res["success"])
        thread_id = res["thread_id"]
        print(f"Created thread ID: {thread_id}")

        # Inaccessible space creation test (e.g. unverified user)
        # Verify access rule properly blocks unauthorized postings
        blocked_res = DiscussionModel.create_thread(
            user_id="invalid_user_id",
            title="Unauthorized Post",
            category="Thesis",
            content="Should be blocked"
        )
        self.assertFalse(blocked_res["success"])
        print(f"Unauthorized post correctly blocked: {blocked_res['message']}")

    def test_04_comments_and_reactions(self):
        print("\n--- Testing Comments & Reactions on Threads & Comments ---")
        threads = DiscussionModel.get_threads(category="General Academic Discussions", user_id="stu_1")
        target_thread = threads[0]["thread_id"]

        # Add comment
        c_res = DiscussionModel.add_comment(target_thread, "stu_2", "Great point, I agree!")
        self.assertTrue(c_res["success"])
        comment_id = c_res["comment_id"]
        print(f"Posted comment ID: {comment_id}")

        # Add reaction to thread
        r1 = DiscussionModel.add_reaction("stu_1", thread_id=target_thread, reaction_type="like")
        self.assertTrue(r1["success"])
        self.assertEqual(r1["action"], "added")
        print(f"Reaction to thread added: {r1}")

        # Toggle reaction to thread -> removes own reaction
        r2 = DiscussionModel.add_reaction("stu_1", thread_id=target_thread, reaction_type="like")
        self.assertTrue(r2["success"])
        self.assertEqual(r2["action"], "removed")
        print(f"Reaction to thread removed on second click (unlike): {r2}")

        # Add reaction to comment
        c_r1 = DiscussionModel.add_reaction("stu_1", comment_id=comment_id, reaction_type="like")
        self.assertTrue(c_r1["success"])
        self.assertEqual(c_r1["action"], "added")
        print(f"Reaction to comment added: {c_r1}")

        # Delete comment
        del_c = DiscussionModel.delete_comment(comment_id, "stu_2")
        self.assertTrue(del_c["success"])
        print("Comment deleted successfully.")

    def test_05_thread_reminders(self):
        print("\n--- Testing Thread Reminders with Specific Date & Time ---")
        threads = DiscussionModel.get_threads(category="General Academic Discussions", user_id="stu_1")
        target_thread = threads[0]["thread_id"]

        remind_at = "2026-08-25 22:30:00"
        rem_res = DiscussionModel.set_reminder(
            thread_id=target_thread,
            user_id="stu_1",
            remind_at=remind_at,
            note="Prepare feedback for study circle"
        )
        self.assertTrue(rem_res["success"])
        reminder_id = rem_res["reminder_id"]
        print(f"Scheduled reminder ID: {reminder_id} for {remind_at}")

        # Fetch user reminders
        user_rems = DiscussionModel.get_user_reminders("stu_1")
        self.assertGreater(len(user_rems), 0)
        print(f"stu_1 reminders count: {len(user_rems)}")

        # Delete reminder
        del_rem = DiscussionModel.delete_reminder(reminder_id, "stu_1")
        self.assertTrue(del_rem["success"])
        print("Reminder deleted/dismissed.")

    def test_06_admin_analytics_and_moderation(self):
        print("\n--- Testing Admin Analytics & Moderation ---")
        analytics = DiscussionModel.get_admin_analytics("admin_1")
        self.assertTrue(analytics["success"])
        stats = analytics["stats"]
        self.assertGreaterEqual(stats["total_threads"], 10)
        self.assertIn("Thesis", stats["spaces"])
        self.assertIn("Projects", stats["spaces"])
        self.assertIn("Internships", stats["spaces"])
        self.assertIn("Defense Preparation", stats["spaces"])
        self.assertIn("General Academic Discussions", stats["spaces"])
        print("Admin discussion analytics:", stats)

        # Admin delete thread
        new_th = DiscussionModel.create_thread("stu_1", "Delete Me", "General Academic Discussions", "Delete body")
        th_id = new_th["thread_id"]
        del_th = DiscussionModel.delete_thread(th_id, "admin_1")
        self.assertTrue(del_th)
        print("Admin moderation delete thread successful.")

if __name__ == "__main__":
    unittest.main()
