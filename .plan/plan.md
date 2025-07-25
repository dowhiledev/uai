# Unified Agent Interface (UAI) — Implementation Plan

This plan breaks down the technical brief into actionable, incremental steps for developing the `uai` Python package. Each phase includes deliverables, goals, and recommended sequencing. Use this as a living roadmap for the initial implementation and future extensibility.

---

## Phase 0: Repository Scaffold
- Create `src/uai/` package directory
- Add `__init__.py`, `adapters/`, and `core/` submodules
- Set up `tests/` and `examples/` directories
- Add `pyproject.toml` and configure basic metadata
- Write initial `README.md` with project purpose and usage

---

## Phase 1: Core Abstractions
- Implement `BaseAdapter` (ABC) with all UAI methods as stubs
- Define `UnifiedAgent` facade class
- Implement `wrap_agent()` with heuristic adapter detection
- Add capability enum and runtime introspection (`supports()`)
- Document error handling (raise `NotImplementedError` for unsupported methods)
- Write unit tests for capability detection and error handling

---

## Phase 2: CrewAI Workflow Adapter
- Implement `CrewAIWorkflowAdapter` subclass
- Integrate with CrewAI’s `crew.execute()` and status polling
- Normalize artifacts to UAI format
- Add integration tests with a minimal CrewAI example
- Document usage and limitations

---

## Phase 3: LangChain Chat Adapter
- Implement `LangChainChatAdapter` for conversational agents
- Support `chat()` and `stream()` via LangChain’s `invoke` and `stream`/`astream`
- Add tests for token streaming and chunking
- Document streaming caveats and compatibility

---

## Phase 4: CrewAI Hybrid Adapter
- Implement `CrewAIHybridAdapter` (inherits workflow adapter)
- Add support for human-in-the-loop (`await_prompt`, `reply`)
- Yield user prompt events during execution
- Test pause/resume flows and reply channel
- Document interactive workflow pattern

---

## Phase 5: LangGraph Workflow Adapter
- Implement `LangGraphWorkflowAdapter` for graph-based workflows
- Integrate with LangGraph’s run submission and polling APIs
- Normalize results and artifacts
- Add integration tests with LangGraph example
- Document workflow orchestration and streaming

---

## Phase 6: FastAPI Reference Server
- Build a FastAPI server exposing all UAI REST endpoints
- Route requests to wrapped agents via UAI facade
- Support SSE for streaming endpoints
- Add OpenAPI docs and example client scripts
- Write end-to-end tests for REST API

---

## Phase 7: Documentation & Example Notebooks
- Create docs site (mkdocs)
- Write API reference and usage guides
- Add example notebooks for CrewAI, LangChain, LangGraph
- Document extensibility and plugin registry

---

## Extensibility & Future Work
- Implement plugin registry (`entry_points = "uai.adapters"`)
- Support batch runs (`run_many`) and stream-of-tasks
- Add telemetry hooks for metrics and monitoring
- Track upstream framework changes for new adapter support

---

## References
- See technical brief for full reference links and rationale
