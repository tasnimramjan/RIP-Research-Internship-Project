import os
from seed import seed_data

DB_PATH = os.path.join(os.path.dirname(__file__), "rip_database.sqlite")

def reseed():
    if os.path.exists(DB_PATH):
        print(f"Removing existing database at {DB_PATH}...")
        os.remove(DB_PATH)
    
    print("Running seed script...")
    seed_data()
    print("Database has been successfully seeded with all fields!")

if __name__ == "__main__":
    reseed()
