import  hashlib
import json
import uuid
import random
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

    print("Seeding database with 20+ generated records per category...")

    # 1. Admin
    admin_id = "admin_1"
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (admin_id, "System Administrator", "admin@univ.edu", hash_pw("password123"), "CSE", "Admin", "Active"))
    cursor.execute("INSERT INTO admins VALUES (?, ?)", (admin_id, "SuperAdmin"))

    # Data Banks
    first_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Niaj", "Olivia", "Peggy", "Sybil", "Trent", "Victor", "Walter", "Yusuf", "Zara", "John", "Jane", "Rahim", "Karim", "Aisha", "Omar", "Fatima", "Sam", "Lucy", "Mike"]
    last_names = ["Smith", "Doe", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Perez", "Ahmed", "Rahman", "Hasan", "Chowdhury", "Khan"]
    departments = ["CSE", "EEE", "BBA", "MNE", "CE"]
    domains_bank = ["Artificial Intelligence", "Machine Learning", "Computer Vision", "Deep Learning", "Medical Imaging", "NLP", "LLMs", "Speech Processing", "Cybersecurity", "Blockchain", "Cloud Security", "IoT", "Robotics", "Embedded Systems", "Data Science", "Bioinformatics", "Quantum Computing", "Software Engineering", "HCI", "Networks", "Cloud Computing", "Augmented Reality", "Virtual Reality"]
    
    # 2. Faculty (20)
    faculties = []
    for i in range(1, 21):
        f_name = f"Dr. {random.choice(first_names)} {random.choice(last_names)}"
        faculties.append({
            "id": f"fac_{i}",
            "name": f_name,
            "email": f"faculty{i}@univ.edu",
            "dept": random.choice(departments),
            "designation": random.choice(["Professor", "Associate Professor", "Assistant Professor", "Lecturer"]),
            "h_index": random.randint(5, 50),
            "domains": random.sample(domains_bank, k=random.randint(2, 4)),
            "slots": random.randint(0, 5),
            "max_capacity": 5,
            "current_students": random.randint(0, 5),
            "min_cgpa": round(random.uniform(3.0, 3.8), 2),
            "available": random.choice([0, 1])
        })
        
    for f in faculties:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (f["id"], f["name"], f["email"], hash_pw("password123"), f["dept"], "Faculty", "Active"))
        cursor.execute("INSERT INTO faculty (faculty_id, designation, h_index, research_domains, remaining_slots, max_capacity, current_students, min_cgpa_req, thesis_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (f["id"], f["designation"], f["h_index"], json.dumps(f["domains"]), f["slots"], f["max_capacity"], f["current_students"], f["min_cgpa"], f["available"]))

    # 3. Students (20)
    students = []
    for i in range(1, 21):
        s_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        students.append({
            "id": f"stu_{i}",
            "name": s_name,
            "email": f"student{i}@univ.edu",
            "dept": random.choice(departments),
            "cgpa": round(random.uniform(2.5, 4.0), 2),
            "interests": random.sample(domains_bank, k=random.randint(2, 4))
        })
        
    for s in students:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (s["id"], s["name"], s["email"], hash_pw("password123"), s["dept"], "Student", "Active"))
        cursor.execute("INSERT INTO students VALUES (?, ?, ?)",
                       (s["id"], s["cgpa"], json.dumps(s["interests"])))

    # 4. Research Labs (20)
    lab_adjectives = ["Advanced", "Smart", "Intelligent", "Applied", "Global", "Cyber", "Autonomous", "NextGen", "Bio", "Quantum"]
    lab_nouns = ["Systems", "Vision", "Data", "Networks", "Robotics", "Analytics", "Security", "Computing", "Hardware", "Materials"]
    labs = []
    for i in range(1, 21):
        fac_id = f"fac_{i}"
        l_name = f"{random.choice(lab_adjectives)} {random.choice(lab_nouns)} Lab"
        labs.append({
            "id": f"lab_{i}",
            "name": l_name,
            "focus": ", ".join(random.sample(domains_bank, k=2)),
            "facilities": ["High-End GPU", "Testbed", "Workstations"],
            "faculty": fac_id,
            "ras": [
                {"id": f"ra_{i}", "title": f"RA in {random.choice(domains_bank)}", "desc": "Assisting with core research.", "stipend": f"${random.randint(400, 800)}/month", "deadline": "2026-12-31"}
            ],
            "projects": [
                {"id": f"lp_{i}", "title": f"Exploring {random.choice(domains_bank)} Techniques"}
            ]
        })
        
    for l in labs:
        cursor.execute("INSERT INTO research_labs VALUES (?, ?, ?, ?, ?)",
                       (l["id"], l["name"], l["focus"], json.dumps(l["facilities"]), l["faculty"]))
        for ra in l["ras"]:
            cursor.execute("INSERT INTO ra_opportunities VALUES (?, ?, ?, ?, ?, ?)",
                           (ra["id"], l["id"], ra["title"], ra["desc"], ra["stipend"], ra["deadline"]))
        for p in l["projects"]:
            cursor.execute("INSERT INTO lab_projects VALUES (?, ?, ?, ?)",
                           (p["id"], l["id"], p["title"], "Ongoing research exploration."))

    # 5. Internship Opportunities (20)
    companies = ["DataTech Inc", "WebSphere Solutions", "RoboTech Labs", "CyberDefend", "AI Innovators", "FinTech Global", "CloudNet", "BioHealth Systems", "EduSmart", "AutoDrive"]
    roles = ["Software Engineer Intern", "Data Analyst Intern", "Machine Learning Intern", "Frontend Intern", "Backend Developer Intern", "Security Analyst Intern", "Product Intern"]
    internships = []
    for i in range(1, 21):
        internships.append({
            "id": f"int_{i}",
            "company": random.choice(companies),
            "title": random.choice(roles),
            "requirements": "Basic programming skills, eagerness to learn.",
            "min_cgpa": round(random.uniform(3.0, 3.5), 1),
            "dept": random.choice(departments),
            "deadline": "2026-10-01",
            "contact_email": f"hr@company{i}.com",
            "contact_phone": "+1 (555) 000-0000",
            "external_url": f"https://company{i}.com/careers"
        })

    for item in internships:
        cursor.execute("INSERT INTO internship_opportunities (opportunity_id, company_name, title, requirements, min_cgpa, department, deadline, contact_email, contact_phone, external_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (item["id"], item["company"], item["title"], item["requirements"], item["min_cgpa"], item["dept"], item["deadline"], item["contact_email"], item["contact_phone"], item["external_url"]))

    # Add sample applications (20)
    for i in range(1, 21):
        cursor.execute("INSERT INTO internship_applications VALUES (?, ?, ?, ?, ?)",
                       (f"app_{i}", f"int_{i}", f"stu_{i}", "Pending", "2026-07-20 10:00:00"))

    # 6. Project Posts (20)
    post_adjectives = ["Autonomous", "AI-Powered", "Smart", "Blockchain-based", "Scalable", "Real-time", "Decentralized", "Cloud-native"]
    post_nouns = ["Quadcopter", "Citation Generator", "Chatbot", "E-commerce Platform", "Healthcare App", "IoT System", "Data Pipeline"]
    posts = []
    for i in range(1, 21):
        posts.append({
            "id": f"post_{i}",
            "student": f"stu_{i}",
            "title": f"{random.choice(post_adjectives)} {random.choice(post_nouns)}",
            "desc": "Looking for teammates to collaborate on this exciting project.",
            "skills": random.sample(["Python", "C++", "Java", "React", "Node.js", "SQL", "Docker", "AWS", "TensorFlow"], k=3),
            "date": "2026-08-01 10:00:00"
        })

    for p in posts:
        cursor.execute("INSERT INTO project_posts VALUES (?, ?, ?, ?, ?, ?)",
                       (p["id"], p["student"], p["title"], p["desc"], json.dumps(p["skills"]), p["date"]))

    # 7. Thesis Groups (20)
    for i in range(1, 21):
        topic = random.choice(domains_bank)
        group_id = f"grp_{i}"
        cursor.execute("INSERT INTO thesis_groups VALUES (?, ?, ?, ?, ?, ?)",
                       (group_id, f"{topic} Study Group", f"Advanced {topic} Research", "A collaborative group working on state of the art.", f"stu_{i}", "2026-08-10 12:00:00"))

    # 8. Research Papers (20)
    paper_adjectives = ["Advanced", "Novel", "Robust", "Scalable", "Efficient", "Deep", "Intelligent", "Automated"]
    paper_nouns = ["Framework", "Algorithm", "Approach", "System", "Architecture", "Methodology", "Analysis", "Evaluation"]
    papers = []
    for i in range(1, 21):
        p_title = f"A {random.choice(paper_adjectives)} {random.choice(paper_nouns)} for {random.choice(domains_bank)}"
        p_authors = [f"{random.choice(first_names)} {random.choice(last_names)}", f"Dr. {random.choice(first_names)} {random.choice(last_names)}"]
        p_domain = random.choice(domains_bank)
        p_year = random.randint(2018, 2026)
        p_abstract = f"This paper presents a {random.choice(paper_adjectives).lower()} {random.choice(paper_nouns).lower()} addressing key challenges in {p_domain}. Experimental results demonstrate significant improvements over state-of-the-art methods."
        # Generate a dummy 4-dimensional vector embedding
        p_vector = [random.random() for _ in range(4)]
        norm = sum(x*x for x in p_vector) ** 0.5
        p_vector = [x/norm for x in p_vector] if norm > 0 else [0.25]*4
        
        papers.append({
            "id": f"paper_{i}",
            "title": p_title,
            "authors": p_authors,
            "domain": p_domain,
            "year": p_year,
            "abstract": p_abstract,
            "vector": p_vector,
            "doi": f"10.1016/j.cs.{p_year}.{random.randint(1000,9999)}",
            "url": f"https://example.com/papers/paper_{i}.pdf"
        })

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
    # 14.     # Feature 16: Research Events & Conferences
    events = [
        {"id": "evt_01", "title": "Annual AI & Machine Learning Symposium", "category": "Conference",
         "organizer": "Department of CSE", "date": "2026-11-15 10:00:00", "location": "Auditorium A",
         "desc": "National conference on AI innovations and research presentations.",
         "link": "https://univ.edu/ml2026", "created_at": "2026-07-20 09:00:00"},
        {"id": "evt_02", "title": "LaTeX Thesis Formatting & Defense Workshop", "category": "Workshop",
         "organizer": "Research Committee", "date": "2026-10-05 14:00:00", "location": "Lab 402",
         "desc": "Hands-on guide to formatting thesis documents and presentation slides.",
         "link": "https://univ.edu/latex-workshop", "created_at": "2026-07-21 11:30:00"}
    ]
    for e in events:
        cursor.execute(
            "INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (e["id"], e["title"], e["category"], e["organizer"], e["date"], e["location"], e["desc"], e["link"], e["created_at"])
        )

    # Feature 18: Real-Time Notification Center
    notifications = [
        {"id": "notif_01", "user": "stu_alice", "type": "Academic", "title": "Thesis Proposal Deadline",
         "message": "Your draft thesis proposal submission is due next week.", "is_read": 0, "created_at": "2026-07-22 08:00:00"},
        {"id": "notif_02", "user": "stu_alice", "type": "Events", "title": "Event Registration Open",
         "message": "Annual AI & Machine Learning Symposium registration is now active.", "is_read": 0, "created_at": "2026-07-22 09:15:00"}
    ]
    for n in notifications:
        cursor.execute(
            "INSERT OR IGNORE INTO notifications (notification_id, user_id, type, title, message, reference_id, sender_id, is_read, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (n["id"], n["user"], n["type"], n["title"], n["message"], None, None, n["is_read"], n["created_at"])
        )
        
           # Feature 17: Admin Logs
    cursor.execute("INSERT OR IGNORE INTO admin_logs VALUES (?, ?, ?, ?)",
                   ("log_01", "Verified Faculty Profile", "fac_rahman", "2026-07-20 10:00:00"))

    # Feature 19: User Tasks
    cursor.execute("INSERT OR IGNORE INTO user_tasks VALUES (?, ?, ?, ?, ?)",
                   ("task_01", "stu_alice", "Submit Thesis First Draft", "2026-09-01", "Pending"))
    cursor.execute("INSERT OR IGNORE INTO user_tasks VALUES (?, ?, ?, ?, ?)",
                   ("task_02", "stu_alice", "Register for AI Symposium", "2026-10-15", "Completed"))

    # Feature 20: FAQ Chatbot Knowledgebase
    cursor.execute("INSERT OR IGNORE INTO faq_chatbot VALUES (?, ?, ?)",
                   ("faq_01", "thesis,supervisor,defence", "To register for a thesis supervisor, check the Smart Supervisor Finder tab and submit your application with your CGPA and research statement."))
    cursor.execute("INSERT OR IGNORE INTO faq_chatbot VALUES (?, ?, ?)",
                   ("faq_02", "internship,job,career", "Internship listings are updated weekly under the Internship Opportunity Portal."))
    conn.commit()
    conn.close()
    print("Database seeded successfully with generated data.")

if __name__ == "__main__":
    seed_data()
    seed_data()
