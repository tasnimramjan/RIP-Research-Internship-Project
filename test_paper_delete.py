import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))
from controllers.paper_controller import PaperController
from models.paper import ResearchPaperModel

class TestPaperDeletion(unittest.TestCase):

    def test_01_admin_delete_paper(self):
        print("\n--- Testing Admin Research Paper Deletion ---")
        
        # 1. Create a paper
        paper_id = ResearchPaperModel.add_paper(
            faculty_id="fac_1",
            title="Quantum Graph Neural Networks for Molecule Discovery",
            authors=["Dr. Alan Turing", "Alice Green"],
            domain="Computer Vision & AI",
            year=2026,
            abstract="Novel molecular graph generation framework."
        )
        self.assertTrue(paper_id.startswith("paper_"))
        print(f"Created research paper: {paper_id}")

        # 2. Student attempt to delete should fail
        stu_del = PaperController.delete_paper("stu_1", {"paper_id": paper_id})
        self.assertFalse(stu_del["success"])
        self.assertIn("Only administrators can delete", stu_del["message"])
        print("Student delete blocked correctly:", stu_del["message"])

        # 3. Admin deletes the paper successfully
        admin_del = PaperController.delete_paper("admin_1", {"paper_id": paper_id})
        self.assertTrue(admin_del["success"])
        print("Admin deleted paper successfully:", admin_del["message"])

        # 4. Verify paper no longer exists
        all_papers = ResearchPaperModel.get_all_papers()
        self.assertFalse(any(p["paper_id"] == paper_id for p in all_papers))
        print("Verified paper removed from database.")

if __name__ == "__main__":
    unittest.main()
