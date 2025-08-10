from fastapi.testclient import TestClient
from unified_agent_interface.app import get_app
import time, os, pathlib

# Ensure examples/.env exists
env_path = pathlib.Path('examples/.env')
print('env exists:', env_path.exists())

client = TestClient(get_app())

payload = {
  "input": "AI trends",
  "params": {
    "agent": "crewai",
    "crewai_module": "examples.crewai_example",
    # You can override inputs here; leaving None to let adapter derive from input
  }
}

r = client.post('/run/', json=payload)
print('create', r.status_code, r.json())
run_id = r.json()['task_id']

status = None
result_text = None
for i in range(60):
    time.sleep(2)
    resp = client.get(f'/run/{run_id}')
    data = resp.json()
    status = data['status']
    print(i, status)
    if status in ('completed','failed'):
        result_text = data.get('result_text')
        break

print('final status:', status)
print('result length:', len(result_text or ''))
if result_text:
    print((result_text[:500] + '...') if len(result_text) > 500 else result_text)