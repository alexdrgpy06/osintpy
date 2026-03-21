import sqlite3
import json

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE profiles (data_json TEXT)")

data1 = {
    "digital_footprint": [1, 2],
    "contacts": {"emails": [1]},
    "news_mentions": [1, 2, 3],
    "risk_score": 60
}
data2 = {
    "digital_footprint": [1],
    "contacts": {},
    "risk_score": 40
}
conn.execute("INSERT INTO profiles VALUES (?)", (json.dumps(data1),))
conn.execute("INSERT INTO profiles VALUES (?)", (json.dumps(data2),))
conn.commit()

cursor = conn.cursor()
cursor.execute("""
    SELECT
        COUNT(*),
        SUM(COALESCE(json_array_length(data_json, '$.digital_footprint'), 0)),
        SUM(COALESCE(json_array_length(data_json, '$.contacts.emails'), 0)),
        SUM(COALESCE(json_array_length(data_json, '$.news_mentions'), 0)),
        SUM(CASE WHEN CAST(json_extract(data_json, '$.risk_score') AS INTEGER) > 50 THEN 1 ELSE 0 END)
    FROM profiles
""")
print(cursor.fetchone())
