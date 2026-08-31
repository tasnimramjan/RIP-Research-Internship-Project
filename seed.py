import hashlib
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
        fac_id = f"fac_{((int(p['id'].split('_')[1]) - 1) % 20) + 1}"
        cursor.execute("INSERT INTO research_papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (p["id"], p["title"], json.dumps(p["authors"]), p["domain"], p["year"], p["abstract"], json.dumps(p["vector"]), p["doi"], p["url"], fac_id))

    # 9. Discussion Threads, Comments, Reactions, and Reminders
    forum_threads_seed = [
        # Thesis
        ("th_101", "fac_1", "Best Practices for Structuring Your Thesis Literature Review", "Thesis", "When drafting the literature review, ensure you categorize previous literature methodologically rather than chronologically. Focus on highlighting research gaps.", "2026-08-15 09:30:00"),
        ("th_102", "stu_1", "Selecting Standard Benchmark Datasets for NLP Thesis", "Thesis", "We are finalizing our dataset choices for NLP transfer learning evaluation. What are the recommended open benchmarks for domain adaptation?", "2026-08-18 14:15:00"),
        # Projects
        ("th_103", "stu_2", "Architecture Choices for Real-Time IoT Data Streaming", "Projects", "For the automated smart monitor project, what streaming pipeline works best: MQTT with Kafka or direct WebSockets?", "2026-08-20 11:00:00"),
        ("th_104", "fac_2", "Capstone Project Evaluation Criteria & Milestones", "Projects", "Please review the semester project rubric. Teams must demonstrate unit testing, clean git commit history, and a deployed demo.", "2026-08-21 16:45:00"),
        # Internships
        ("th_105", "stu_3", "Tips for Technical Coding & System Design Interviews", "Internships", "Sharing key takeaways from recent technical screening interviews at DataTech Inc and WebSphere Solutions. Focus heavily on DSA and clean coding!", "2026-08-22 10:20:00"),
        ("th_106", "fac_3", "Industry Internship Credit Transfer Guidelines", "Internships", "Students currently undergoing summer internships must submit their mid-term supervisor evaluations by next week.", "2026-08-23 15:30:00"),
        # Defense Preparation
        ("th_107", "fac_4", "Defense Committee Expectations & Presentation Slide Guidelines", "Defense Preparation", "Keep defense presentations under 20 minutes. Allocate at least 8 minutes to your experimental evaluation and novel contributions.", "2026-08-24 13:00:00"),
        ("th_108", "stu_1", "Defense Q&A: Common Questions on Methodology & Limitations", "Defense Preparation", "Compiling a checklist of questions previous defense candidates faced regarding methodology threats to validity.", "2026-08-25 18:00:00"),
        # General Academic Discussions
        ("th_109", "stu_4", "Balancing Coursework, Lab Research, and Project Deadlines", "General Academic Discussions", "How do you manage time when balancing 4 courses alongside lab research work? What scheduling techniques work best?", "2026-08-26 12:00:00"),
        ("th_110", "fac_5", "Academic Integrity & Proper Citation Formats for Publications", "General Academic Discussions", "A reminder to all students to use verified reference managers (e.g. BibTeX, Zotero) and avoid plagiarism when preparing submissions.", "2026-08-27 10:00:00")
    ]

    for t in forum_threads_seed:
        cursor.execute("INSERT INTO discussion_threads (thread_id, user_id, title, category, content, created_at) VALUES (?, ?, ?, ?, ?, ?)", t)

    # Comments
    comments_seed = [
        ("c_201", "th_101", "stu_1", "This is very helpful, Professor. Should we also include comparative summary tables in Chapter 2?", "2026-08-15 10:15:00"),
        ("c_202", "th_101", "fac_1", "Yes, comparative taxonomy tables are strongly recommended by the review committee.", "2026-08-15 10:45:00"),
        ("c_203", "th_102", "fac_1", "Look into GLUE, SuperGLUE, and domain-specific benchmarks like BioASQ if you are evaluating specialized texts.", "2026-08-18 15:00:00"),
        ("c_204", "th_103", "stu_1", "MQTT with EMQX broker or Kafka has worked very reliably for our IoT testbed experiments.", "2026-08-20 12:30:00"),
        ("c_205", "th_105", "stu_2", "Great tips! Practicing mock interviews on LeetCode Mediums made a huge difference.", "2026-08-22 11:05:00"),
        ("c_206", "th_107", "stu_1", "Thank you Dr.! Should demo recordings be embedded directly in the slide deck?", "2026-08-24 14:10:00"),
        ("c_207", "th_107", "fac_4", "Yes, have a backup local video recording in case live internet connection lags.", "2026-08-24 14:30:00"),
        ("c_208", "th_109", "stu_2", "Time-blocking 2 hours early in the morning specifically for research helped me stay consistent.", "2026-08-26 13:20:00")
    ]

    for c in comments_seed:
        cursor.execute("INSERT INTO forum_comments (comment_id, thread_id, user_id, content, created_at) VALUES (?, ?, ?, ?, ?)", c)

    # Reactions (on threads and comments)
    reactions_seed = [
        ("th_101", None, "stu_1", "like"),
        ("th_101", None, "stu_2", "like"),
        ("th_101", None, "fac_2", "like"),
        ("th_102", None, "fac_1", "like"),
        ("th_103", None, "stu_3", "like"),
        ("th_105", None, "stu_1", "like"),
        ("th_107", None, "stu_1", "like"),
        ("th_107", None, "stu_4", "like"),
        (None, "c_201", "fac_1", "like"),
        (None, "c_203", "stu_1", "like"),
        (None, "c_205", "stu_3", "like")
    ]

    for r in reactions_seed:
        cursor.execute("INSERT INTO forum_reactions (thread_id, comment_id, user_id, reaction_type) VALUES (?, ?, ?, ?)", r)

    # Sample Reminders
    reminders_seed = [
        ("rem_301", "th_107", "stu_1", "2026-08-25 22:30:00", "Review defense slide guidelines before advisor meeting", 0),
        ("rem_302", "th_101", "stu_1", "2026-09-05 10:00:00", "Complete literature review synthesis chapter", 0)
    ]

    for rem in reminders_seed:
        cursor.execute("INSERT INTO thread_reminders (reminder_id, thread_id, user_id, remind_at, note, is_triggered) VALUES (?, ?, ?, ?, ?, ?)", rem)

    conn.commit()
    conn.close()
    print("Database seeded successfully with generated data and discussion forums.")

if __name__ == "__main__":
    seed_data()
