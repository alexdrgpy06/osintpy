import sqlite3
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Optional

try:
    from thefuzz import fuzz
except ImportError:
    class _FuzzFallback:
        @staticmethod
        def ratio(a, b): return 100 if a.lower() == b.lower() else 0
        @staticmethod
        def partial_ratio(a, b): return 100 if a.lower() in b.lower() or b.lower() in a.lower() else 0
    fuzz = _FuzzFallback()

class ProfilePersistenceAgent:
    """
    Manages the persistent storage of consolidated OSINT profiles.
    Includes SQLite persistence and Ocas-Scout Journaling.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "data", "profiles.db")
    JOURNALS_DIR = os.path.join(BASE_DIR, "journals")

    @classmethod
    def init_db(cls):
        if not os.path.exists(os.path.dirname(cls.DB_PATH)):
            os.makedirs(os.path.dirname(cls.DB_PATH))
        conn = sqlite3.connect(cls.DB_PATH)
        # Main Profiles Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                type TEXT,
                query TEXT,
                full_name TEXT,
                data_json TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        # User Feedback Table for Refinement
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT,
                field TEXT,
                incorrect_value TEXT,
                correct_value TEXT,
                comment TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    @classmethod
    def save_feedback(cls, profile_id: str, field: str, incorrect_value: str, correct_value: str, comment: str):
        cls.init_db()
        now = datetime.now().isoformat()
        conn = sqlite3.connect(cls.DB_PATH)
        conn.execute("""
            INSERT INTO feedback (profile_id, field, incorrect_value, correct_value, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (profile_id, field, incorrect_value, correct_value, comment, now))
        conn.commit()
        conn.close()

    @classmethod
    def get_all_feedback(cls):
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "profile_id": r[1],
                "field": r[2],
                "incorrect_value": r[3],
                "correct_value": r[4],
                "comment": r[5],
                "status": r[6],
                "created_at": r[7]
            } for r in rows
        ]

    @classmethod
    def merge_and_save(cls, profile_id: str, p_type: str, query: str, new_data: dict):
        cls.init_db()
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        # 1. Try to find existing by query
        cursor.execute("SELECT id, data_json FROM profiles WHERE query = ?", (query,))
        row = cursor.fetchone()
        
        # 2. If not found, try CI/RUC match
        new_ci = new_data.get("identity", {}).get("ci")
        new_ruc = new_data.get("fiscal", {}).get("ruc")
        new_name = new_data.get("identity", {}).get("full_name", "").strip().upper()
        
        if not row and (new_ci or new_ruc or (new_name and new_name != "DESCONOCIDO")):
            cursor.execute("SELECT id, data_json, full_name FROM profiles")
            all_profiles = cursor.fetchall()
            for p_id, p_data_str, p_full_name in all_profiles:
                try:
                    p_data = json.loads(p_data_str)
                except:
                    continue
                existing_ci = p_data.get("identity", {}).get("ci")
                existing_ruc = p_data.get("fiscal", {}).get("ruc")
                existing_name = (p_full_name or "").strip().upper()
                
                matched = False
                if new_ci and existing_ci and new_ci == existing_ci:
                    matched = True
                elif new_ruc and existing_ruc and new_ruc == existing_ruc:
                    matched = True
                elif new_name and new_name != "DESCONOCIDO" and existing_name and existing_name != "DESCONOCIDO":
                    if new_name == existing_name or fuzz.ratio(new_name, existing_name) >= 90:
                        matched = True
                
                if matched:
                    row = (p_id, p_data_str)
                    profile_id = p_id
                    break
        
        if row:
            existing_data = json.loads(row[1])
            try:
                from services.identity_resolver import IdentityResolver
                final_data = IdentityResolver.merge_profiles(existing_data, new_data)
                final_data.pop("news_mentions", None)
            except Exception as e:
                import logging
                logging.getLogger("kuarahy").error(f"Error merging profiles: {e}")
                final_data = new_data
                final_data.pop("news_mentions", None)
        else:
            final_data = new_data
            final_data.pop("news_mentions", None)

        data_str = json.dumps(final_data)
        full_name = final_data.get("identity", {}).get("full_name", query)
        
        conn.execute("""
            INSERT OR REPLACE INTO profiles (id, type, query, full_name, data_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM profiles WHERE id=?), ?), ?)
        """, (profile_id, p_type, query, full_name, data_str, profile_id, now, now))
        conn.commit()
        conn.close()

    @classmethod
    def get_global_stats(cls) -> Dict:
        """Returns aggregate metrics for the landing dashboard."""
        if not os.path.exists(cls.DB_PATH):
            return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}
            
        try:
            with sqlite3.connect(cls.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data_json FROM profiles") # Corrected column name to data_json
                rows = cursor.fetchall()
                
                total_profiles = len(rows)
                total_nodes = 0
                total_emails = 0
                total_phones = 0
                
                for row in rows:
                    if not row[0]: continue
                    try:
                        data = json.loads(row[0])
                        total_nodes += len(data.get("digital_footprint", []))
                        total_emails += len(data.get("contacts", {}).get("emails", []))
                        total_phones += len(data.get("contacts", {}).get("phones", []))
                    except: pass
                    
                return {
                    "total_profiles": total_profiles,
                    "total_nodes": total_nodes,
                    "total_emails": total_emails,
                    "total_phones": total_phones
                }
        except Exception as e:
            import logging # Added import for logging
            logger = logging.getLogger("kuarahy") # Defined logger
            logger.error(f"Error getting stats: {e}")
            return {"total_profiles": 0, "total_nodes": 0, "total_emails": 0, "total_phones": 0}

    @classmethod
    def save_override(cls, profile_id: str, new_data: dict):
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        now = datetime.now().isoformat()

        # Load existing profile to merge correctly if not full replacement
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()

        if row:
            try:
                existing_data = json.loads(row[0])
            except:
                existing_data = {}
        else:
            existing_data = {}

        # Recursive merge or full overwrite (we assume the payload is a full object representing the state)
        # However, to be safe, if we get partial data, we update. For a profile editor, it's usually a full dump.
        existing_data.update(new_data)

        data_str = json.dumps(existing_data)
        full_name = existing_data.get("identity", {}).get("full_name", "")
        conn.execute("""
            UPDATE profiles 
            SET data_json = ?, full_name = ?, updated_at = ?
            WHERE id = ?
        """, (data_str, full_name, now, profile_id))
        conn.commit()
        conn.close()

    @classmethod
    def get_all_profiles(cls):
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "type": r[1],
                "query": r[2],
                "full_name": r[3],
                "data": json.loads(r[4]),
                "updated_at": r[6]
            } for r in rows
        ]

    @classmethod
    def get_profile_by_id(cls, profile_id: str):
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "type": row[1],
                "query": row[2],
                "full_name": row[3],
                "data": json.loads(row[4]),
                "created_at": row[5],
                "updated_at": row[6]
            }
        return None

    @classmethod
    def get_metrics(cls):
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM profiles")
        rows = cursor.fetchall()
        conn.close()
        
        total_profiles = len(rows)
        total_socials = 0
        total_emails = 0
        total_news = 0
        high_risk_count = 0
        
        for r in rows:
            data = json.loads(r[0])
            total_socials += len(data.get("digital_footprint", []))
            total_emails += len(data.get("contacts", {}).get("emails", []))
            total_news += len(data.get("news_mentions", []))
            if data.get("risk_score", 0) > 50:
                high_risk_count += 1
                
        return {
            "total_profiles": total_profiles,
            "total_social_accounts": total_socials,
            "total_emails_leaked": total_emails,
            "total_news_mentions": total_news,
            "high_risk_profiles": high_risk_count
        }

    @classmethod
    def get_global_radar(cls):
        """
        Analyzes all stored profiles to find cross-linkages.
        Returns a giant graph of Targets connected by shared nodes.
        """
        profiles = cls.get_all_profiles()
        nodes_dict = {}
        edges = []
        
        for p in profiles:
            target_id = f"target_{p['id']}"
            name = p.get('full_name') or p.get('query')
            nodes_dict[target_id] = {
                "id": target_id, "label": name, "type": "Target", "group": "identity"
            }
            
            data = p.get("data", {})
            p_nodes = data.get("graph", {}).get("nodes", [])
            for n in p_nodes:
                # OPTIMIZATION: Only build cross-profile links for highly critical intelligence vectors.
                # Avoid linking by individual photos or unique social URLs that create noise.
                if n["type"] not in ["email", "phone", "location", "organization", "company", "funcionario_publico", "address"]:
                    continue
                
                shared_id = f"{n['type']}_{n['label']}"
                if shared_id not in nodes_dict:
                    nodes_dict[shared_id] = {
                        "id": shared_id, "label": n["label"], "sublabel": n.get("sublabel", ""),
                        "type": n["type"], "group": n["group"]
                    }
                
                # Check if edge already exists
                edge = {"source": target_id, "target": shared_id, "label": "VÍNCULO DETECTADO"}
                if edge not in edges:
                    edges.append(edge)
                
        # Filter out nodes that have only 1 connection (i.e., not shared with ANY other target) to strictly reveal cross-profile connections
        edge_counts = {}
        for e in edges:
            edge_counts[e["target"]] = edge_counts.get(e["target"], 0) + 1
            
        shared_targets = {k for k, v in edge_counts.items() if v > 1}
        
        final_nodes = [n for n in nodes_dict.values() if n["type"] == "Target" or n["id"] in shared_targets]
        final_edges = [e for e in edges if e["target"] in shared_targets]
        
        return {
            "nodes": final_nodes,
            "edges": final_edges
        }

    @classmethod
    def ocas_scout_journal(cls, profile_id: str, metrics: dict):
        """
        Writes a JSON journal for the run following the ocas-scout spec v1.3.
        """
        profile = cls.get_profile_by_id(profile_id)
        if not profile:
            return
            
        now = datetime.now()
        date_folder = now.strftime("%Y-%m-%d")
        journal_dir = os.path.join(cls.JOURNALS_DIR, "ocas-scout", date_folder)
        os.makedirs(journal_dir, exist_ok=True)
        
        journal_path = os.path.join(journal_dir, f"{profile_id}.json")
        tmp_path = journal_path + ".tmp"
        
        journal_data = {
            "run_identity": {
                "run_id": profile_id,
                "role": "champion",
                "skill_name": "osintpy-core",
                "skill_version": "5.0.0",
                "timestamp_start": profile.get("created_at", now.isoformat()),
                "timestamp_end": profile.get("updated_at", now.isoformat()),
                "journal_spec_version": "1.3",
                "journal_type": "research"
            },
            "runtime": {
                "model": "deterministic-omni-resolver",
                "provider": "local",
                "node": "osintpy-v5-engine"
            },
            "input": {
                "command": profile["query"]
            },
            "metrics": metrics
        }
        
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(journal_data, f, indent=2, ensure_ascii=False)
            
        os.rename(tmp_path, journal_path)
        return journal_path
