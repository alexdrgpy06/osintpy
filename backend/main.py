from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import uuid
import asyncio
import os
import sys
import logging
from datetime import datetime

# Pathing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from services.task_manager import task_manager
from services.health_check import SystemValidator
from agents.persistence import ProfilePersistenceAgent
from agents.feedback_processor import FeedbackProcessor

from contextlib import asynccontextmanager

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("kuarahy")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("[STARTUP] Motor de inteligencia Kuarahy v4 activo.")
    yield
    # Shutdown logic
    logger.info("[SHUTDOWN] Cerrando procesos del motor.")

app = FastAPI(
    title="OSINTPY v4 — Kuarahy Intelligence Engine",
    description="Motor de Inteligencia Táctica Paraguaya",
    lifespan=lifespan
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class SearchQuery(BaseModel):
    ci_ruc: str = ""
    nombre: str = ""
    alias: str = ""
    email: str = ""
    telefono: str = ""
    notas_adicionales: str = ""

class FeedbackRequest(BaseModel):
    profile_id: str
    field: str
    incorrect_value: str
    correct_value: str
    comment: str

@app.post("/api/search")
async def search(q: SearchQuery, background_tasks: BackgroundTasks):
    # Fetch health for the runner to be "health-aware"
    health = await SystemValidator.get_full_health()
    task_manager._health_status = health 
    
    task_id = task_manager.create_task(q.model_dump()) # Pass the multi-vector object
    background_tasks.add_task(task_manager.run_engine, task_id)
    return {"task_id": task_id}

@app.get("/api/search/status/{task_id}")
async def status(task_id: str):
    task = task_manager.get_task_status(task_id)
    if task.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/profiles")
async def profiles():
    return ProfilePersistenceAgent.get_all_profiles()

@app.get("/api/profiles/search")
async def search_profiles(q: str):
    profiles = ProfilePersistenceAgent.get_all_profiles()
    results = []
    for p in profiles:
        name = p["identity"].get("full_name", "").lower()
        if q.lower() in name:
            results.append({"id": p.get("id"), "name": p["identity"].get("full_name")})
    return results

@app.get("/api/stats")
async def get_system_stats():
    stats = ProfilePersistenceAgent.get_global_stats()
    return stats

@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: str):
    profile = ProfilePersistenceAgent.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/api/profiles/{profile_id}")
async def override_profile(profile_id: str, payload: dict):
    ProfilePersistenceAgent.save_override(profile_id, payload)
    return {"status": "success", "message": "Dossier actualizado correctamente."}

@app.get("/api/metrics")
async def metrics():
    return ProfilePersistenceAgent.get_metrics()

@app.get("/api/radar")
async def radar():
    return ProfilePersistenceAgent.get_global_radar()

@app.post("/api/feedback")
async def save_feedback(f: FeedbackRequest):
    ProfilePersistenceAgent.save_feedback(f.profile_id, f.field, f.incorrect_value, f.correct_value, f.comment)
    return {"status": "success", "message": "Feedback received."}

@app.get("/api/refinement-log")
async def get_refinement_log():
    report = await FeedbackProcessor.generate_refinement_report()
    return {"report": report}

class ProfileUpdateRequest(BaseModel):
    task_id: str
    rejected_nodes: List[Dict] = []
    new_seeds: List[str] = []
    verified_nodes: List[Dict] = []

@app.post("/api/search/update")
async def update_search(req: ProfileUpdateRequest, background_tasks: BackgroundTasks):
    logger.info(f"[UPDATE] Recibida solicitud de refinamiento para: {req.task_id}")
    # Build a proper target_data dict for the new task
    first_seed = req.new_seeds[0] if req.new_seeds else "Refinement"
    seed_target = {"alias": first_seed}
    task_id = task_manager.create_task(seed_target)
    
    task_manager.tasks[task_id]["rejected_nodes"] = req.rejected_nodes
    task_manager.tasks[task_id]["new_seeds"] = req.new_seeds
    task_manager.tasks[task_id]["verified_nodes"] = req.verified_nodes
    task_manager.tasks[task_id]["original_task_id"] = req.task_id
    
    logger.info(f"[UPDATE] Nueva tarea recursiva creada: {task_id}")
    background_tasks.add_task(task_manager.run_engine, task_id)
    return {"task_id": task_id, "message": "Inteligencia recursiva iniciada..."}

@app.get("/api/profiles/{profile_id}/refresh")
async def refresh_profile(profile_id: str, background_tasks: BackgroundTasks):
    profile = ProfilePersistenceAgent.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    target_data = profile.get("target_data") or {"alias": profile.get("query")}
    task_id = task_manager.create_task(target_data)
    background_tasks.add_task(task_manager.run_engine, task_id)
    return {"task_id": task_id, "message": "Refrescando datos del perfil..."}

@app.get("/health_basic")
async def health_basic():
    return {"status": "online", "version": "4.0.1"}

@app.get("/api/health")
async def api_health():
    return await SystemValidator.get_full_health()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
