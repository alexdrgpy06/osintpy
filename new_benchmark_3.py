import time
import json
import sqlite3
import os
from backend.agents.persistence import ProfilePersistenceAgent

def run_benchmark_old():
    start = time.time()
    for _ in range(100):
        stats = ProfilePersistenceAgent.get_metrics()
    end = time.time()
    print(f"Old Stats: {stats}")
    print(f"Old Time taken: {end - start:.4f} seconds")
    return end - start

def get_metrics_new():
    ProfilePersistenceAgent.init_db()
    DB_PATH = ProfilePersistenceAgent.DB_PATH
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*),
                    SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.digital_footprint')), 0) ELSE 0 END),
                    SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.contacts.emails')), 0) ELSE 0 END),
                    SUM(CASE WHEN json_valid(data_json) THEN COALESCE(json_array_length(json_extract(data_json, '$.news_mentions')), 0) ELSE 0 END),
                    SUM(CASE WHEN json_valid(data_json) AND CAST(json_extract(data_json, '$.risk_score') AS INTEGER) > 50 THEN 1 ELSE 0 END)
                FROM profiles
                WHERE data_json IS NOT NULL
            """)

            row = cursor.fetchone()

            if row:
                return {
                    "total_profiles": row[0] or 0,
                    "total_social_accounts": int(row[1] or 0),
                    "total_emails_leaked": int(row[2] or 0),
                    "total_news_mentions": int(row[3] or 0),
                    "high_risk_profiles": int(row[4] or 0)
                }
            return {
                "total_profiles": 0,
                "total_social_accounts": 0,
                "total_emails_leaked": 0,
                "total_news_mentions": 0,
                "high_risk_profiles": 0
            }
    except Exception as e:
        import logging
        logger = logging.getLogger("kuarahy")
        logger.error(f"Error getting metrics: {e}")
        return {
            "total_profiles": 0,
            "total_social_accounts": 0,
            "total_emails_leaked": 0,
            "total_news_mentions": 0,
            "high_risk_profiles": 0
        }

def run_benchmark_new():
    start = time.time()
    for _ in range(100):
        stats = get_metrics_new()
    end = time.time()
    print(f"New Stats: {stats}")
    print(f"New Time taken: {end - start:.4f} seconds")
    return end - start

if __name__ == "__main__":
    t_old = run_benchmark_old()
    t_new = run_benchmark_new()
    print(f"Improvement: {t_old / t_new:.2f}x faster")
