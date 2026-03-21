import sqlite3
import json
import time
import os
import random

from backend.agents.persistence import ProfilePersistenceAgent

DB_PATH = ProfilePersistenceAgent.DB_PATH
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

ProfilePersistenceAgent.init_db()

conn = sqlite3.connect(DB_PATH)

print("Generating 50,000 dummy rows...")
batch = []
for i in range(50000):
    data = {
        "digital_footprint": [1] * random.randint(0, 10),
        "contacts": {
            "emails": [1] * random.randint(0, 3),
            "phones": [1] * random.randint(0, 3)
        }
    }
    batch.append((str(i), "person", "q", "name", json.dumps(data), "2023-01-01", "2023-01-01"))

conn.executemany("INSERT INTO profiles (id, type, query, full_name, data_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", batch)
conn.commit()
conn.close()

# Profile get_global_stats (old way)
print("Testing baseline get_global_stats()...")
start = time.time()
res_old = ProfilePersistenceAgent.get_global_stats()
end = time.time()
old_time = end - start
print(f"Old time: {old_time:.4f}s")
print("Result:", res_old)

# Profile get_global_stats (new way)
def get_global_stats_new():
    if not os.path.exists(ProfilePersistenceAgent.DB_PATH):
        return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}

    try:
        with sqlite3.connect(ProfilePersistenceAgent.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(*),
                    SUM(COALESCE(json_array_length(data_json, '$.digital_footprint'), 0)),
                    SUM(COALESCE(json_array_length(data_json, '$.contacts.emails'), 0)),
                    SUM(COALESCE(json_array_length(data_json, '$.contacts.phones'), 0))
                FROM profiles
                WHERE data_json IS NOT NULL
            """)
            row = cursor.fetchone()

            if row and row[0] > 0:
                return {
                    "total_profiles": row[0] or 0,
                    "total_nodes": row[1] or 0,
                    "total_emails": row[2] or 0,
                    "total_phones": row[3] or 0
                }
            return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}
    except Exception as e:
        import logging
        logger = logging.getLogger("kuarahy")
        logger.error(f"Error getting stats: {e}")
        return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}

print("Testing new get_global_stats()...")
start = time.time()
res_new = get_global_stats_new()
end = time.time()
new_time = end - start
print(f"New time: {new_time:.4f}s")
print("Result:", res_new)
assert res_old["total_profiles"] == res_new["total_profiles"]
assert res_old["total_nodes"] == res_new["total_nodes"]
assert res_old["total_emails"] == res_new["total_emails"]
assert res_old["total_phones"] == res_new["total_phones"]
print(f"Results match! Improvement: {old_time / new_time:.2f}x faster")
