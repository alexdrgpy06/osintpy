import sqlite3
import json
from backend.agents.persistence import ProfilePersistenceAgent

conn = sqlite3.connect(ProfilePersistenceAgent.DB_PATH)
cursor = conn.cursor()

# Make a profile where data_json is not an object or not valid JSON
cursor.execute("INSERT INTO profiles (id, type, query, full_name, data_json, created_at, updated_at) VALUES (?, 'type', 'query', 'name', ?, '2023-01-01', '2023-01-01')", ("1003", "invalid json"))
cursor.execute("INSERT INTO profiles (id, type, query, full_name, data_json, created_at, updated_at) VALUES (?, 'type', 'query', 'name', ?, '2023-01-01', '2023-01-01')", ("1004", "null"))
conn.commit()

try:
    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.digital_footprint')), 0)),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.contacts.emails')), 0)),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.contacts.phones')), 0))
        FROM profiles
        WHERE data_json IS NOT NULL AND json_valid(data_json)
    """)
    print(cursor.fetchone())
except Exception as e:
    print(f"Error: {e}")

conn.close()
