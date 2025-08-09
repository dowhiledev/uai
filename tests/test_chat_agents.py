from __future__ import annotations

from fastapi.testclient import TestClient


def test_chat_echo_next(client: TestClient):
    res = client.post('/chat/next', json={'user_input': 'hello'})
    assert res.status_code == 200
    data = res.json()
    assert 'state' in data and isinstance(data['state'], dict)
    assert data['artifacts'] == []


def test_chat_multi_turn_and_artifact(client: TestClient):
    # First call increments to turn 1
    state = {}
    res = client.post('/chat/next?agent=chat_multi', json={'user_input': 'first', 'state': state})
    assert res.status_code == 200
    state = res.json()['state']
    assert state.get('turn') == 1

    # Second call with keyword should emit an artifact and increment turn
    res = client.post('/chat/next?agent=chat_multi', json={'user_input': 'emit artifact please', 'state': state})
    assert res.status_code == 200
    data = res.json()
    assert data['state'].get('turn') == 2
    assert isinstance(data['artifacts'], list) and len(data['artifacts']) >= 1


def test_chat_session_with_agent_selection(client: TestClient):
    # Create session
    res = client.post('/chat/')
    assert res.status_code == 200
    sid = res.json()['session_id']

    # Send message using chat_multi agent
    res = client.post(f'/chat/{sid}?agent=chat_multi', json={'user_input': 'hello session'})
    assert res.status_code == 200

    # Verify messages contain both user and assistant replies
    res = client.get(f'/chat/{sid}/messages')
    assert res.status_code == 200
    msgs = res.json()
    assert len(msgs) >= 2
    assert msgs[0]['role'] == 'user'
    assert msgs[-1]['role'] == 'assistant'

