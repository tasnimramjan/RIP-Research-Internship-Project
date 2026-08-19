import hashlib
import json
import uuid
import os
from db import get_db, init_db

def hash_pw(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def seed_data():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        print("Database already seeded.")
        conn.close()
        return

    print("Seeding database...")

    # 1. Admin
    admin_id = "admin_1"
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (admin_id, "System Administrator", "admin@univ.edu", hash_pw("password123"), "CSE", "Admin", "Active"))
    cursor.execute("INSERT INTO admins VALUES (?, ?)", (admin_id, "SuperAdmin"))

    # 2. Faculty
    faculties = [
        {
            "id": "fac_rahman",
            "name": "Dr. M. Rahman",
            "email": "rahman@univ.edu",
            "dept": "CSE",
            "designation": "Professor",
            "h_index": 24,
            "domains": ["Computer Vision", "Deep Learning", "Medical Imaging"],
            "slots": 3,
            "min_cgpa": 3.5,
            "available": 1
        },
        {
            "id": "fac_chowdhury",
            "name": "Dr. S. Chowdhury",
            "email": "chowdhury@univ.edu",
            "dept": "CSE",
            "designation": "Associate Professor",
            "h_index": 18,
            "domains": ["NLP", "LLMs", "Speech Processing"],
            "slots": 2,
            "min_cgpa": 3.2,
            "available": 1
        },
        {
            "id": "fac_hasan",
            "name": "Dr. Tanvir Hasan",
            "email": "hasan@univ.edu",
            "dept": "EEE",
            "designation": "Assistant Professor",
            "h_index": 12,
            "domains": ["IoT", "Robotics", "Embedded Systems"],
            "slots": 4,
            "min_cgpa": 3.0,
            "available": 1
        },
        {
            "id": "fac_ahmed",
            "name": "Dr. Nazmul Ahmed",
            "email": "ahmed@univ.edu",
            "dept": "CSE",
            "designation": "Professor",
            "h_index": 30,
            "domains": ["Cybersecurity", "Blockchain", "Cloud Security"],
            "slots": 0,
            "min_cgpa": 3.7,
            "available": 0
        }
    ]

    for f in faculties:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (f["id"], f["name"], f["email"], hash_pw("password123"), f["dept"], "Faculty", "Active"))
        cursor.execute("INSERT INTO faculty VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (f["id"], f["designation"], f["h_index"], json.dumps(f["domains"]), f["slots"], f["min_cgpa"], f["available"]))

    # 3. Students
    students = [
        {
            "id": "stu_alice",
            "name": "Alice Vance",
            "email": "alice@univ.edu",
            "dept": "CSE",
            "cgpa": 3.85,
            "interests": ["Deep Learning", "Computer Vision", "Medical Imaging"]
        },
        {
            "id": "stu_bob",
            "name": "Bob Miller",
            "email": "bob@univ.edu",
            "dept": "CSE",
            "cgpa": 3.40,
            "interests": ["NLP", "LLMs", "Chatbots"]
        },
        {
            "id": "stu_charlie",
            "name": "Charlie Green",
            "email": "charlie@univ.edu",
            "dept": "EEE",
            "cgpa": 3.15,
            "interests": ["IoT", "Robotics", "Automation"]
        },
        {
            "id": "stu_david",
            "name": "David Kim",
            "email": "david@univ.edu",
            "dept": "CSE",
            "cgpa": 3.65,
            "interests": ["Cybersecurity", "Software Engineering"]
        }
    ]

    for s in students:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (s["id"], s["name"], s["email"], hash_pw("password123"), s["dept"], "Student", "Active"))
        cursor.execute("INSERT INTO students VALUES (?, ?, ?)",
                       (s["id"], s["cgpa"], json.dumps(s["interests"])))

    # 4. Research Labs & RAs
    labs = [
        {
            "id": "lab_ai",
            "name": "Vision & Intelligence Lab",
            "focus": "Computer Vision, Medical Image Analysis, Multi-modal Learning",
            "facilities": ["NVIDIA A100 GPU Cluster", "Eye Tracker", "High-Res Medical Scanners"],
            "faculty": "fac_rahman",
            "ras": [
                {"id": "ra_1", "title": "Graduate RA in Medical Vision", "desc": "Develop 3D segmentation algorithms for MRI datasets.", "stipend": "$500/month", "deadline": "2026-08-15"}
            ],
            "projects": [
                {"id": "lp_1", "title": "Automated Brain Tumor Segmentation in MRI Scan Data"}
            ]
        },
        {
            "id": "lab_nlp",
            "name": "Language Processing & Knowledge Lab",
            "focus": "Natural Language Processing, LLM Evaluation, Speech Systems",
            "facilities": ["DGX Station", "Annotated Multilingual Corpus", "Audio Recording Studio"],
            "faculty": "fac_chowdhury",
            "ras": [
                {"id": "ra_2", "title": "NLP Research Assistant for LLM Alignment", "desc": "Collect and curate preference datasets for open-source LLM fine-tuning.", "stipend": "$450/month", "deadline": "2026-08-20"}
            ],
            "projects": [
                {"id": "lp_2", "title": "Low-Resource Multilingual Sentiment & Summarization Engine"}
            ]
        },
        {
            "id": "lab_robotics",
            "name": "Embedded & Autonomous Systems Lab",
            "focus": "Robotics, Microcontrollers, Smart IoT Systems",
            "facilities": ["3D Printers", "Drone Flying Testbed", "High-Precision Oscilloscopes"],
            "faculty": "fac_hasan",
            "ras": [],
            "projects": [
                {"id": "lp_3", "title": "Autonomous Drone Swarm Navigation in Obstacle Fields"}
            ]
        }
    ]

    for l in labs:
        cursor.execute("INSERT INTO research_labs VALUES (?, ?, ?, ?, ?)",
                       (l["id"], l["name"], l["focus"], json.dumps(l["facilities"]), l["faculty"]))
        for ra in l["ras"]:
            cursor.execute("INSERT INTO ra_opportunities VALUES (?, ?, ?, ?, ?, ?)",
                           (ra["id"], l["id"], ra["title"], ra["desc"], ra["stipend"], ra["deadline"]))
        for p in l["projects"]:
            cursor.execute("INSERT INTO lab_projects VALUES (?, ?, ?, ?)",
                           (p["id"], l["id"], p["title"], "Ongoing research exploration."))

    # 5. Internship Opportunities
    internships = [
        {
            "id": "int_1",
            "company": "DataTech Inc",
            "title": "Machine Learning Engineer Intern",
            "requirements": "Proficiency in Python, PyTorch/TensorFlow, OpenCV, and basic SQL.",
            "min_cgpa": 3.3,
            "dept": "CSE",
            "deadline": "2026-08-30",
            "contact_email": "internships@datatech.io",
            "contact_phone": "+1 (415) 882-4400",
            "external_url": "https://careers.datatech.io/ml-intern"
        },
        {
            "id": "int_2",
            "company": "WebSphere Solutions",
            "title": "Full-Stack Software Engineering Intern",
            "requirements": "Hands-on experience with JavaScript/Node.js, HTML/CSS, REST APIs, Git.",
            "min_cgpa": 3.0,
            "dept": "CSE",
            "deadline": "2026-09-10",
            "contact_email": "hr@websphere.com",
            "contact_phone": "+1 (212) 334-7701",
            "external_url": "https://websphere.com/careers/fullstack-intern"
        },
        {
            "id": "int_3",
            "company": "RoboTech Labs",
            "title": "Embedded Systems Engineer Intern",
            "requirements": "C/C++ programming, microcontrollers (STM32/ESP32), circuit debugging.",
            "min_cgpa": 3.2,
            "dept": "EEE",
            "deadline": "2026-08-25",
            "contact_email": "jobs@robotechlabs.com",
            "contact_phone": "+1 (650) 555-0192",
            "external_url": "https://robotechlabs.com/internships"
        }
    ]

    for item in internships:
        cursor.execute("INSERT INTO internship_opportunities (opportunity_id, company_name, title, requirements, min_cgpa, department, deadline, contact_email, contact_phone, external_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (item["id"], item["company"], item["title"], item["requirements"], item["min_cgpa"], item["dept"], item["deadline"], item["contact_email"], item["contact_phone"], item["external_url"]))

    # Add sample application
    cursor.execute("INSERT INTO internship_applications VALUES (?, ?, ?, ?, ?)",
                   ("app_1", "int_1", "stu_alice", "Pending", "2026-07-20 10:00:00"))

    # 6. Project Posts (Teammate Finder)
    posts = [
        {
            "id": "post_1",
            "student": "stu_charlie",
            "title": "Autonomous Quadcopter Drone with Real-Time Obstacle Avoidance",
            "desc": "Building a custom quadcopter using ROS and computer vision sensors to autonomously navigate indoors.",
            "skills": ["Arduino", "C++", "Computer Vision", "ROS", "Hardware Fabrication"],
            "date": "2026-07-21 14:30:00"
        },
        {
            "id": "post_2",
            "student": "stu_bob",
            "title": "AI-Powered Thesis Citation Generator & Reference Assistant",
            "desc": "Developing a web platform that parses research papers and automatically formats citations into IEEE, APA, and MLA styles.",
            "skills": ["Python", "FastAPI", "JavaScript", "NLP", "SQLite"],
            "date": "2026-07-22 09:15:00"
        }
    ]

    for p in posts:
        cursor.execute("INSERT INTO project_posts VALUES (?, ?, ?, ?, ?, ?)",
                       (p["id"], p["student"], p["title"], p["desc"], json.dumps(p["skills"]), p["date"]))

    # 7. Research Papers & Vector Embeddings
    papers = [
        {
            "id": "paper_1",
            "title": "Deep Residual Learning for Image Recognition",
            "authors": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
            "domain": "Computer Vision",
            "year": 2016,
            "abstract": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.",
            "vector": [0.92, 0.15, 0.05, 0.44],
            "doi": "10.1109/CVPR.2016.90",
            "url": "https://arxiv.org/abs/1512.03385"
        },
        {
            "id": "paper_2",
            "title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
            "domain": "NLP",
            "year": 2017,
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose the Transformer, a model architecture relying entirely on self-attention.",
            "vector": [0.12, 0.95, 0.88, 0.20],
            "doi": "10.5555/3295222.3295349",
            "url": "https://arxiv.org/abs/1706.03762"
        },
        {
            "id": "paper_3",
            "title": "YOLOv8: Real-Time Object Detection & Instance Segmentation Architecture",
            "authors": ["Glenn Jocher", "Ayush Chaurasia", "Jing Qiu"],
            "domain": "Computer Vision",
            "year": 2023,
            "abstract": "YOLOv8 provides state-of-the-art accuracy and speed for object detection, segmentation, and classification, introducing a new backbone and anchor-free detection head.",
            "vector": [0.88, 0.22, 0.10, 0.50],
            "doi": "10.48550/arXiv.2305.09972",
            "url": "https://github.com/ultralytics/ultralytics"
        },
        {
            "id": "paper_4",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
            "domain": "NLP",
            "year": 2019,
            "abstract": "We introduce a new language representation model called BERT, designed to pre-train deep bidirectional representations from unlabeled text.",
            "vector": [0.10, 0.90, 0.92, 0.15],
            "doi": "10.18653/v1/N19-1423",
            "url": "https://arxiv.org/abs/1810.04805"
        }
    ]

    for p in papers:
        cursor.execute("INSERT INTO research_papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (p["id"], p["title"], json.dumps(p["authors"]), p["domain"], p["year"], p["abstract"], json.dumps(p["vector"]), p["doi"], p["url"]))

    # 8. Discussion Threads
    threads = [
        {
            "id": "th_1",
            "user": "stu_alice",
            "title": "How to choose a suitable Thesis Supervisor for Computer Vision?",
            "category": "Thesis",
            "content": "Hi everyone! I am looking for advice on contacting faculty members for thesis supervision in Computer Vision. What CGPA and preliminary literature review should I prepare?",
            "date": "2026-07-20 11:00:00"
        },
        {
            "id": "th_2",
            "user": "stu_bob",
            "title": "Tips for Internship Technical Interviews at DataTech & Software Companies",
            "category": "Internships",
            "content": "Can senior students share their experience with technical coding tests and system design questions for ML engineering internships?",
            "date": "2026-07-21 16:45:00"
        },
        {
            "id": "th_3",
            "user": "fac_rahman",
            "title": "Best Practices for Preparing a Thesis Defense Presentation Slide Deck",
            "category": "Defense Preparation",
            "content": "Students preparing for upcoming defense sessions: focus heavily on methodology, performance metrics comparison against baseline literature, and clear problem formulation.",
            "date": "2026-07-22 10:30:00"
        }
    ]

    for t in threads:
        cursor.execute("INSERT INTO discussion_threads VALUES (?, ?, ?, ?, ?, ?)",
                       (t["id"], t["user"], t["title"], t["category"], t["content"], t["date"]))

    # Thread Comments
    cursor.execute("INSERT INTO forum_comments VALUES (?, ?, ?, ?, ?)",
                   ("c_1", "th_1", "fac_rahman", "Make sure your fundamental linear algebra and PyTorch basics are clear before requesting a meeting!", "2026-07-20 11:30:00"))
    cursor.execute("INSERT INTO forum_reactions VALUES (NULL, ?, ?, ?)",
                   ("th_1", "stu_alice", "like"))
    cursor.execute("INSERT INTO forum_reactions VALUES (NULL, ?, ?, ?)",
                   ("th_1", "stu_bob", "helpful"))

    # 9. Thesis Groups
    groups = [
        {
            "id": "grp_1",
            "name": "Medical Imaging Thesis Study Circle",
            "topic": "Brain MRI & Microscopic Image Segmentation",
            "desc": "A collaboration group for senior students working on medical AI, deep learning models, and datasets.",
            "creator": "stu_alice",
            "date": "2026-07-19 14:00:00"
        },
        {
            "id": "grp_2",
            "name": "LLM & Prompt Engineering Research Circle",
            "topic": "Large Language Models & Bangla NLP",
            "desc": "Exploring transformer architectures, open-source model fine-tuning, and evaluation metrics.",
            "creator": "stu_bob",
            "date": "2026-07-20 09:30:00"
        }
    ]

    for g in groups:
        cursor.execute("INSERT INTO thesis_groups VALUES (?, ?, ?, ?, ?, ?)",
                       (g["id"], g["name"], g["topic"], g["desc"], g["creator"], g["date"]))
        cursor.execute("INSERT INTO thesis_group_members VALUES (NULL, ?, ?, ?)",
                       (g["id"], g["creator"], g["date"]))

    # 10. Sample Messages
    cursor.execute("INSERT INTO chat_messages VALUES (?, ?, ?, ?, ?, ?)",
                   ("msg_1", "stu_alice", "fac_rahman", None, "Respected Sir, I am interested in joining your Vision & Intelligence Lab for my undergraduate thesis.", "2026-07-22 11:00:00"))
    cursor.execute("INSERT INTO chat_messages VALUES (?, ?, ?, ?, ?, ?)",
                   ("msg_2", "fac_rahman", "stu_alice", None, "Hello Alice, your CGPA is impressive. Please review our lab's MRI Segmentation paper and send me your proposal outline.", "2026-07-22 11:05:00"))

    # 11. Project Teammates
    cursor.execute("INSERT INTO project_teammates VALUES (NULL, ?, ?, ?)", ("post_1", "stu_alice", "Accepted"))
    cursor.execute("INSERT INTO project_teammates VALUES (NULL, ?, ?, ?)", ("post_2", "stu_charlie", "Pending"))

    # 12. Thread Reminders
    cursor.execute("INSERT INTO thread_reminders VALUES (?, ?, ?, ?, ?, ?)",
                   ("rem_1", "th_1", "stu_alice", "2026-08-25 10:00:00", "Review presentation", 0))

    # 13. Group Chat Messages
    cursor.execute("INSERT INTO chat_messages VALUES (?, ?, ?, ?, ?, ?)",
                   ("msg_3", "stu_alice", None, "grp_1", "Hey team, let's start the literature review this weekend.", "2026-07-23 10:00:00"))

    conn.commit()
    conn.close()
    print("Database seeded successfully with initial data.")

if __name__ == "__main__":
    seed_data()
