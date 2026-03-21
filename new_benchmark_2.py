import time
import json
import sqlite3
import os
from backend.agents.persistence import ProfilePersistenceAgent

def setup_db():
    if os.path.exists(ProfilePersistenceAgent.DB_PATH):
        os.remove(ProfilePersistenceAgent.DB_PATH)
    ProfilePersistenceAgent.init_db()

    conn = sqlite3.connect(ProfilePersistenceAgent.DB_PATH)
    cursor = conn.cursor()

    # Insert 10000 dummy profiles
    dummy_data = {
        "digital_footprint": [1, 2, 3, 4, 5],
        "contacts": {
            "emails": ["test1@test.com", "test2@test.com"],
            "phones": ["123456789", "987654321", "555555555"]
        }
    }
    dummy_json = json.dumps(dummy_data)

    cursor.executemany(
        "INSERT INTO profiles (id, type, query, full_name, data_json, created_at, updated_at) VALUES (?, 'type', 'query', 'name', ?, '2023-01-01', '2023-01-01')",
        [(str(i), dummy_json) for i in range(10000)]
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_db()
