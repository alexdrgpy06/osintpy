import asyncio
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.task_manager import task_manager

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run_query(query, q_type):
    print(f"\n--- INICIANDO TEST DEEP DIVE OSINT: {query} ({q_type}) ---")
    task_id = task_manager.create_task(query, q_type)
    print(f"Tarea creada: {task_id}")
    
    await task_manager.run_engine(task_id)
    
    status = task_manager.get_task_status(task_id)
    print(f"Status: {status['status']}")
    print(f"Nombre: {status['profile'].get('identity', {}).get('full_name', 'N/A')}")
    print(f"Resumen Gemini:\n{status['profile'].get('summary', 'N/A')}")
    print(f"Nodos descubiertos: {len(status.get('found_nodes', []))}")
    for node in status.get('found_nodes', []):
        val = node.get('value', str(node.get('data', '')))
        print(f" - [{node['type']}] {node['source']}: {val[:80]}")

async def main():
    await run_query("3415404", "ci")
    await run_query("Alejandro Ramirez", "username")
    await run_query("alexdrgpy06", "username")

if __name__ == "__main__":
    asyncio.run(main())
