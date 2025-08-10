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
- Agents are configured via `kosmos.toml` using an adapter per framework.
- Endpoints map to those defined in `idea.md` and are ready for expansion.

Agent Configuration
------------------
- Place a `kosmos.toml` at project root (or set `KOSMOS_TOML` env var). Example:

  ```toml
  [agent]
  runtime = "callable"          # or "crewai"
  entrypoint = "examples.simple_entrypoint:run"
  ```

- Supported runtimes:
  - "callable": imports `module:attr` and calls it with `{ input, params }`, storing return value in `result_text`.
  - "crewai": imports `module:attr` as a Crew and calls `crew.kickoff(inputs={ topic: <input> })` in a background thread.

- The app loads this config on startup and uses it for all `/run` requests.
