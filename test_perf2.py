import sqlite3
import json
import time
import os
import random

DB_PATH = "data/profiles.db"
os.makedirs("data", exist_ok=True)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE profiles (data_json TEXT)")

# Generate 50000 profiles for realistic DB size load testing
print("Generating 50,000 dummy rows...")
# batch insertions
batch = []
for i in range(50000):
    data = {
        "digital_footprint": [1] * random.randint(0, 10),
        "contacts": {"emails": [1] * random.randint(0, 3)},
        "news_mentions": [1] * random.randint(0, 5),
        "risk_score": random.randint(0, 100)
    }
    batch.append((json.dumps(data),))

conn.executemany("INSERT INTO profiles VALUES (?)", batch)
conn.commit()
conn.close()

from backend.agents.persistence import ProfilePersistenceAgent

# Profile get_metrics (old way)
print("Testing baseline get_metrics()...")
start = time.time()
res_old = ProfilePersistenceAgent.get_metrics()
end = time.time()
print(f"Old time: {end - start:.4f}s")
print("Result:", res_old)

# Profile get_metrics (new way)
def get_metrics_new():
    conn = sqlite3.connect(ProfilePersistenceAgent.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(COALESCE(json_array_length(data_json, '$.digital_footprint'), 0)),
            SUM(COALESCE(json_array_length(data_json, '$.contacts.emails'), 0)),
            SUM(COALESCE(json_array_length(data_json, '$.news_mentions'), 0)),
            SUM(CASE WHEN CAST(json_extract(data_json, '$.risk_score') AS INTEGER) > 50 THEN 1 ELSE 0 END)
        FROM profiles
        WHERE data_json IS NOT NULL
    """)
    row = cursor.fetchone()
    conn.close()

    if row and row[0] > 0:
        return {
            "total_profiles": row[0] or 0,
            "total_social_accounts": row[1] or 0,
            "total_emails_leaked": row[2] or 0,
            "total_news_mentions": row[3] or 0,
            "high_risk_profiles": row[4] or 0
        }
    return {
        "total_profiles": 0,
        "total_social_accounts": 0,
        "total_emails_leaked": 0,
        "total_news_mentions": 0,
        "high_risk_profiles": 0
    }

print("Testing new get_metrics()...")
start = time.time()
res_new = get_metrics_new()
end = time.time()
print(f"New time: {end - start:.4f}s")
print("Result:", res_new)
assert res_old["total_profiles"] == res_new["total_profiles"]
assert res_old["total_social_accounts"] == res_new["total_social_accounts"]
assert res_old["total_emails_leaked"] == res_new["total_emails_leaked"]
assert res_old["total_news_mentions"] == res_new["total_news_mentions"]
assert res_old["high_risk_profiles"] == res_new["high_risk_profiles"]
print("Results match!")
