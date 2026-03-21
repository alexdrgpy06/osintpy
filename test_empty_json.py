import sqlite3
import json
from backend.agents.persistence import ProfilePersistenceAgent

def setup_db():
    conn = sqlite3.connect(ProfilePersistenceAgent.DB_PATH)
    cursor = conn.cursor()

    # Insert profiles missing some fields
    dummy_data_1 = {
        "digital_footprint": [1, 2],
    }
    dummy_data_2 = {
        "contacts": {
            "emails": ["test1@test.com"]
        }
    }
    dummy_data_3 = {}

    cursor.executemany(
        "INSERT INTO profiles (id, type, query, full_name, data_json, created_at, updated_at) VALUES (?, 'type', 'query', 'name', ?, '2023-01-01', '2023-01-01')",
        [(str(1000 + i), json.dumps(d)) for i, d in enumerate([dummy_data_1, dummy_data_2, dummy_data_3])]
    )
    conn.commit()

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.digital_footprint')), 0)),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.contacts.emails')), 0)),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.contacts.phones')), 0))
        FROM profiles
        WHERE data_json IS NOT NULL
    """)
    print(cursor.fetchone())
    conn.close()

if __name__ == "__main__":
    setup_db()
