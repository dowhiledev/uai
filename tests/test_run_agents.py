from __future__ import annotations

import time

from fastapi.testclient import TestClient


def test_run_simple_completes(client: TestClient):
    # Create simple run
    res = client.post('/run/', json={'input': 'process this', 'params': {'agent': 'run_simple'}})
    assert res.status_code == 200
    task_id = res.json()['task_id']

    # Poll until completed (bounded wait)
    status = None
    for _ in range(6):
        r = client.get(f'/run/{task_id}')
        assert r.status_code == 200
        status = r.json()['status']
        if status == 'completed':
            break
        time.sleep(1)
    assert status == 'completed'


def test_run_input_required_flow(client: TestClient):
    # Create run that waits for input
    res = client.post('/run/', json={'params': {'agent': 'run_input_required'}})
    assert res.status_code == 200
    task_id = res.json()['task_id']

    # Initially waiting for input
    r = client.get(f'/run/{task_id}')
    assert r.status_code == 200
    assert r.json()['status'] == 'waiting_input'

    # Provide input and ensure it transitions to running → completed
    r = client.post(f'/run/{task_id}/input', json={'input': 'user decision'})
    assert r.status_code == 200

    status = None
    for _ in range(6):
        r = client.get(f'/run/{task_id}')
        assert r.status_code == 200
        status = r.json()['status']
        if status == 'completed':
            break
        time.sleep(1)
    assert status == 'completed'


def test_run_logs_append(client: TestClient):
    # Create simple run, then append a log entry
    res = client.post('/run/', json={'params': {'agent': 'run_simple'}})
    assert res.status_code == 200
    task_id = res.json()['task_id']

    # Append log
    r = client.post(f'/run/{task_id}/logs', json={"level": "INFO", "message": "starting"})
    assert r.status_code == 200

    # Verify status includes logs
    r = client.get(f'/run/{task_id}')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get('logs'), list)
    assert any(log.get('message') == 'starting' for log in data['logs'])

