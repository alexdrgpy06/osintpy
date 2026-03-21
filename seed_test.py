import sqlite3
import os

db_path = 'backend/data/padron_py.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)
conn.execute("CREATE TABLE IF NOT EXISTS personas (ci TEXT PRIMARY KEY, nombre TEXT, apellido TEXT, distrito TEXT, local_votacion TEXT)")
conn.execute("INSERT OR REPLACE INTO personas (ci, nombre, apellido, distrito, local_votacion) VALUES ('3415404', 'ALEJANDRO', 'RAMIREZ', 'ASUNCION', 'COLEGIO NACIONAL')")
conn.commit()
conn.close()

ruc_path = 'backend/data/ruc_py.db'
conn = sqlite3.connect(ruc_path)
conn.execute("CREATE TABLE IF NOT EXISTS ruc_data (ruc TEXT PRIMARY KEY, razon_social TEXT, estado TEXT, dv TEXT)")
conn.execute("INSERT OR REPLACE INTO ruc_data (ruc, razon_social, estado, dv) VALUES ('3415404', 'ALEJANDRO RAMIREZ', 'ACTIVO', '0')")
conn.commit()
conn.close()
print("Real Test Data Seeded: 3415404 - Alejandro Ramirez")
