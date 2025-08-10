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

CrewAI Integration
------------------
- A `crewai` run agent adapter is provided to wrap an existing CrewAI `Crew`.
- Usage example:
  - `POST /run/` with body:
    `{ "params": { "agent": "crewai", "crewai_module": "examples.crewai_example", "crewai_inputs": { "topic": "AI trends" } } }`
- The adapter lazily imports the module specified by `crewai_module`, expects it to expose a `crew` instance, and calls `crew.kickoff(inputs=...)` in a background thread.
- If CrewAI is not installed or the module import fails, the task will transition to `failed` with an error message in `result_text`.
