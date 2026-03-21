import httpx
import asyncio
import time

async def run_test():
    async with httpx.AsyncClient() as client:
        # Start search
        print("Starting search for alexdrgpy06...")
        r = await client.post('http://localhost:8000/api/search', json={'query': 'alexdrgpy06', 'type': 'username'})
        task_id = r.json()['task_id']
        print(f"Task ID: {task_id}")
        
        # Poll for results
        for _ in range(30):
            status_r = await client.get(f'http://localhost:8000/api/search/status/{task_id}')
            data = status_r.json()
            print(f"Status: {data['status']} | Progress: {data['progress']}%")
            if data['status'] == 'completed':
                print("Search Completed!")
                print("Profile Summary:", data['profile']['summary'])
                print("Discovered Nodes:", len(data['found_nodes']))
                break
            time.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except Exception as e:
        print(f"Error: {e}. Make sure the backend is running.")
