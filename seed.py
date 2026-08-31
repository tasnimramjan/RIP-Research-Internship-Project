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
        cursor.execute("INSERT INTO research_papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (p["id"], p["title"], json.dumps(p["authors"]), p["domain"], p["year"], p["abstract"], json.dumps(p["vector"]), p["doi"], p["url"]))

    conn.commit()
    conn.close()
    print("Database seeded successfully with generated data.")

if __name__ == "__main__":
    seed_data()
    seed_data()
