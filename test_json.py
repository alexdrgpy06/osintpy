import sqlite3
from backend.agents.persistence import ProfilePersistenceAgent

conn = sqlite3.connect(ProfilePersistenceAgent.DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT
        COUNT(*),
        SUM(json_array_length(json_extract(data_json, '$.digital_footprint'))),
        SUM(json_array_length(json_extract(data_json, '$.contacts.emails'))),
        SUM(json_array_length(json_extract(data_json, '$.contacts.phones')))
    FROM profiles
    WHERE data_json IS NOT NULL
""")
print(cursor.fetchone())
conn.close()
