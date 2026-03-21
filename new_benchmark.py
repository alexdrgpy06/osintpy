import time
import json
import sqlite3
import os
from backend.agents.persistence import ProfilePersistenceAgent

def run_benchmark_old():
    start = time.time()
    for _ in range(100):
        stats = ProfilePersistenceAgent.get_global_stats()
    end = time.time()
    print(f"Old Stats: {stats}")
    print(f"Old Time taken: {end - start:.4f} seconds")
    return end - start

def get_global_stats_new():
    """Returns aggregate metrics for the landing dashboard."""
    DB_PATH = ProfilePersistenceAgent.DB_PATH
    if not os.path.exists(DB_PATH):
        return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*),
                    SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.digital_footprint')), 0) ELSE 0 END),
                    SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.contacts.emails')), 0) ELSE 0 END),
                    SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.contacts.phones')), 0) ELSE 0 END)
                FROM profiles
                WHERE data_json IS NOT NULL
            """)

            row = cursor.fetchone()

            if row:
                return {
                    "total_profiles": row[0] or 0,
                    "total_nodes": int(row[1] or 0),
                    "total_emails": int(row[2] or 0),
                    "total_phones": int(row[3] or 0)
                }
            return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}
    except Exception as e:
        import logging
        logger = logging.getLogger("kuarahy")
        logger.error(f"Error getting stats: {e}")
        return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}

def run_benchmark_new():
    start = time.time()
    for _ in range(100):
        stats = get_global_stats_new()
    end = time.time()
    print(f"New Stats: {stats}")
    print(f"New Time taken: {end - start:.4f} seconds")
    return end - start

if __name__ == "__main__":
    t_old = run_benchmark_old()
    t_new = run_benchmark_new()
    print(f"Improvement: {t_old / t_new:.2f}x faster")
