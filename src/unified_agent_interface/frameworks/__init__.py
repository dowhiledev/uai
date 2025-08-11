from __future__ import annotations

from typing import Dict

from .base import RuntimeAdapter
from .crewai import CrewAIAdapter
from .callable import CallableAdapter


_adapters: Dict[str, RuntimeAdapter] = {
    "crewai": CrewAIAdapter(),
    "callable": CallableAdapter(),
}


def get_adapter(runtime: str) -> RuntimeAdapter:
    rt = (runtime or "").lower()
    if rt in _adapters:
        return _adapters[rt]
    raise ValueError(f"Unsupported runtime: {runtime}")

