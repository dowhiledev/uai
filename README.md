Unified Agent Interface (UAI)
=============================

Scaffolded FastAPI service that exposes chat and run endpoints with pluggable components and in-memory storage. This is a foundation to build the full UAI described in `idea.md`.

Quickstart
----------
- Install: `pip install -e .`
- Run API: `uai serve --host 0.0.0.0 --port 8000`
- Open docs: visit `http://localhost:8000/docs`

Structure
---------
- `src/unified_agent_interface/app.py`: FastAPI app factory.
- `src/unified_agent_interface/api/`: Routers for `/chat` and `/run`.
- `src/unified_agent_interface/models/`: Pydantic models and schemas.
- `src/unified_agent_interface/components/`: Pluggable agents and storage.

Notes
-----
- Storage is in-memory for now; swap with Postgres/Redis-backed implementations later.
- Agent is a simple echo stub; replace with framework-specific adapters.
- Endpoints map to those defined in `idea.md` and are ready for expansion.
