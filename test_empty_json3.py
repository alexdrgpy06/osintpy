import sqlite3
import json
from backend.agents.persistence import ProfilePersistenceAgent

conn = sqlite3.connect(ProfilePersistenceAgent.DB_PATH)
cursor = conn.cursor()

# Try without json_valid just in case it's slow or not available
try:
    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.digital_footprint')), 0) ELSE 0 END),
            SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.contacts.emails')), 0) ELSE 0 END),
            SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.contacts.phones')), 0) ELSE 0 END)
        FROM profiles
        WHERE data_json IS NOT NULL
    """)
    res = cursor.fetchone()
    print("Using json_valid:", res)
except Exception as e:
    print(f"Error: {e}")

try:
    # See if json_extract returns null when invalid
    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.digital_footprint')), 0)),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.contacts.emails')), 0)),
            SUM(COALESCE(json_array_length(json_extract(data_json, '$.contacts.phones')), 0))
        FROM profiles
        WHERE data_json IS NOT NULL
    """)
    res = cursor.fetchone()
    print("Without json_valid:", res)
except Exception as e:
    print(f"Error without json_valid: {e}")

conn.close()
