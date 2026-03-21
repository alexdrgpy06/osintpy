from celery import Celery
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ensure backend dir is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("osintpy_tasks", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True, name="tasks.run_osint_engine")
def run_osint_engine_task(self, query: str, query_type: str):
    """
    REAL-TIME ORCHESTRATOR in Celery
    Runs tools, streams logs, and consolidates results.
    """
    from agents.osint_tools import OSINTToolAgent
    from agents.py_gov import ParaguayDataAgent
    from agents.persistence import ProfilePersistenceAgent
    from services.identity_resolver import IdentityResolver

    current_logs = []
    consolidated_results = []
    
    def log_callback(line: str):
        # We don't want to overflow the state, so we keep last 50 logs for live view
        # But we could also just append and let the front-end handle it
        # However, Celery state is stored in Redis, so keeping it reasonable is good.
        # We'll just update the task state.
        self.update_state(state='PROGRESS', meta={
            'logs': current_logs[-20:], # Send last 20 logs for UI
            'progress': min(len(current_logs) // 2, 95), # Fake progress based on log count
            'found_nodes': consolidated_results
        })

    try:
        current_logs.append(f"[INIT] Iniciando motor táctico para {query}...")
        log_callback("")

        # 1. Government Data (Paraguay) if CI/RUC
        if query_type in ["ci", "ruc"]:
            current_logs.append(f"[GOV] Consultando registros de Paraguay...")
            gov_hits = ParaguayDataAgent.search_all(query) # Assume this exists
            for hit in gov_hits:
                consolidated_results.append({"type": "identity", "source": "PY_GOV", "data": hit})
            log_callback("")

        # 2. Global OSINT Tools
        if query_type == "username":
            # Sherlock
            OSINTToolAgent.run_sherlock_live(query, log_callback, current_logs, consolidated_results)
            # Blackbird
            OSINTToolAgent.run_blackbird_live(query, log_callback, current_logs, consolidated_results)
            # Toutatis
            OSINTToolAgent.run_toutatis_live(query, log_callback, current_logs, consolidated_results)

        elif query_type == "email":
            OSINTToolAgent.run_holehe_live(query, log_callback, current_logs, consolidated_results)

        # 3. Final Consolidation
        profile = IdentityResolver.consolidate_profile(current_logs, consolidated_results)
        
        # Save to DB
        ProfilePersistenceAgent.save_profile(self.request.id, query_type, query, profile)
        
        return {
            "status": "completed",
            "progress": 100,
            "logs": current_logs,
            "profile": profile
        }
        
    except Exception as e:
        import traceback
        error_msg = f"[ERROR] Engine failure: {str(e)}\n{traceback.format_exc()}"
        current_logs.append(error_msg)
        return {"status": "failed", "error": str(e), "logs": current_logs}
