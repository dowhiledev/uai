# Unified Agent Interface (UAI)

A thin, opinionated wrapper for Python agent frameworks (CrewAI, LangChain, LangGraph, Letta, Nomos, etc.), exposing a unified interface for client-serving concerns.

## Quickstart
```python
from unified_agent_interface import wrap_agent
agent = wrap_agent(my_framework_agent)
```

## Supported Frameworks
- CrewAI
- LangChain
- LangGraph
- Letta
- Nomos

## Extensibility
- Plugin registry for external adapters (`unified_agent_interface.adapters`)

## License
MIT (see LICENSE)