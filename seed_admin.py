import sqlite3
import hashlib
import uuid
import sys
import getpass
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rip_database.sqlite")

def create_admin():
    email = input("Enter admin email: ").strip()
    password = getpass.getpass("Enter admin password: ").strip()

    if not email or not password:
        print("Error: Email and password are required.")
        sys.exit(1)

    admin_id = str(uuid.uuid4())[:8]
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (user_id, name, email, password_hash, department, role, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (admin_id, "System Admin", email, hashed_password, "Admin", "Admin", "Active")
        )
        cursor.execute(
            "INSERT INTO admins (admin_id, admin_level) VALUES (?, ?)",
            (admin_id, "SuperAdmin")
        )
        conn.commit()
        print(f"Admin account created successfully with email '{email}'.")
    except sqlite3.IntegrityError:
        print("Error: An account with this email already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("--- R.I.P Platform Admin Seeder ---")
    create_admin()
