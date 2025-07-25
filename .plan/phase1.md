# Phase 1: Core Abstractions — Detailed Considerations

This document outlines all considerations, design decisions, and best practices for implementing the core abstractions of the Unified Agent Interface (UAI) Python package. Use this as a checklist and reference for Phase 1 development.

---

## 1. Goals & Scope
- Establish the foundational abstractions for all agent adapters and the unified interface.
- Ensure extensibility, clear error handling, and runtime capability introspection.
- Provide a robust base for future adapter and REST API development.

## 2. Key Components
- **BaseAdapter (ABC):**
  - Abstract base class for all adapters.
  - Defines all UAI methods as stubs: `chat`, `stream`, `run`, `status`, `results`, `artifacts`, `await_prompt`, `reply`.
  - Attributes: `framework`, `type` (conversational, workflow, interactive_workflow), `capabilities` (set of supported methods).
  - Enforce NotImplementedError for unsupported methods with standardized error payload.
- **UnifiedAgent (Facade):**
  - Wraps an adapter and exposes only supported capabilities.
  - Provides `supports(capability: str)` for runtime introspection.
  - Delegates calls to the underlying adapter, raising errors for unsupported methods.
- **wrap_agent (Factory):**
  - Heuristically detects agent type and returns a `UnifiedAgent` with the correct adapter.
  - Supports extension via plugin registry (entry points).
- **Capability Enum:**
  - Centralized definition of all supported capabilities.
  - Used for introspection and branching in client code.

## 3. Error Handling
- All unsupported methods must raise `NotImplementedError` with `{ "error": "capability_not_supported" }`.
- Document error contract for downstream consumers and REST API alignment.

## 4. Extensibility
- Design for easy addition of new adapters and capabilities.
- Ensure plugin registry (entry points) can register external adapters.
- Document how to extend BaseAdapter and register new adapters.

## 5. Testing
- Write unit tests for:
  - Capability detection (`supports`)
  - Error handling for unsupported methods
  - Adapter selection via `wrap_agent`
- Use mock agents/adapters for isolated testing.

## 6. Implementation Steps
- Define `BaseAdapter` ABC with all required methods and attributes.
- Implement `UnifiedAgent` facade class.
- Implement `wrap_agent` factory with heuristic detection and plugin support.
- Create capability enum and runtime introspection logic.
- Add initial unit tests for all abstractions.
- Document public API and error contracts in README.

## 7. Milestones & Validation
- All abstractions implemented and tested.
- Adapter selection and capability introspection work as expected.
- Error handling is robust and standardized.
- Ready for integration with first real adapter (CrewAIWorkflowAdapter in Phase 2).

---

## Checklist
- [ ] BaseAdapter ABC defined
- [ ] UnifiedAgent facade implemented
- [ ] wrap_agent factory implemented
- [ ] Capability enum created
- [ ] Error handling standardized
- [ ] Unit tests for abstractions
- [ ] Extensibility documented
- [ ] Milestone validated

---

## Notes
- Focus on clean, extensible design and robust error handling.
- Avoid framework-specific logic; keep abstractions generic.
- Use this document to guide and review Phase 1 implementation.
