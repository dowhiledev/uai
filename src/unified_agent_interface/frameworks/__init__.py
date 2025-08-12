from __future__ import annotations

from typing import Dict

from .base import RuntimeAdapter
from .crewai import CrewAIAdapter
from .callable import CallableAdapter
from .langchain import LangChainAdapter


_adapters: Dict[str, RuntimeAdapter] = {
    "crewai": CrewAIAdapter(),
    "callable": CallableAdapter(),
    "langchain": LangChainAdapter(),
}


def get_adapter(runtime: str) -> RuntimeAdapter:
    rt = (runtime or "").lower()
    if rt in _adapters:
        return _adapters[rt]
    raise ValueError(f"Unsupported runtime: {runtime}")
