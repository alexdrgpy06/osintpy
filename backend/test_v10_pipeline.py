import asyncio
import os
import sys
from services.task_manager import task_manager
import json

async def test_v10_pipeline():
    print("--- OSINTPY v10: Hyper-Velocity Pipeline Integration Test ---")
    
    # Mock health for high-speed execution
    task_manager._health_status = {
        "osint_binaries": {
            "sherlock": "INSTALLED (/usr/bin/sherlock)",
            "maigret": "INSTALLED (/usr/bin/maigret)",
            "social-analyzer": "INSTALLED (/usr/bin/social-analyzer)"
        },
        "civic_apis": {
            "TSJE (Padrón)": "ONLINE",
            "SET (RUC)": "ONLINE"
        }
    }
    
    target_data = {
        "alias": "alexzena",
        "nombre": "Alexandra Zena",
        "email": "test@osintpy.py",
        "notas_adicionales": "Investigación táctica de prueba v10"
    }
    
    task_id = task_manager.create_task(target_data)
    print(f"Task Created: {task_id}")
    
    # Run the engine
    print("Launching Hyper-Velocity Engine (asyncio.gather)...")
    await task_manager.run_engine(task_id)
    
    task = task_manager.get_task_status(task_id)
    print(f"Task Status: {task['status']}")
    
    profile = task.get("profile")
    if profile:
        print(f"Name: {profile['identity'].get('full_name')}")
        print(f"Risk: {profile.get('risk_score')}")
        print(f"Certainty: {profile.get('certainty_score')}")
        print(f"AI Summary v10: {profile.get('ai_summary_v10', 'N/A')[:150]}...")
        
        # Verify parallel results exist
        if task.get("found_nodes"):
            print(f"Nodes found: {len(task['found_nodes'])}")
    
    assert task['status'] == "completed"
    print("\n--- TEST PASSED: Hyper-Velocity Pipeline is OPERATIONAL ---")

if __name__ == "__main__":
    asyncio.run(test_v10_pipeline())
