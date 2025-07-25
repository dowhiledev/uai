from abc import ABC, abstractmethod
from typing import Any, Set

class BaseAdapter(ABC):
    """
    Abstract base class for all agent adapters in Unified Agent Interface.
    Defines the normalized interface and capability contract.
    """
    framework: str  # e.g., 'CrewAI', 'LangChain', etc.
    type: str       # 'conversational', 'workflow', 'interactive_workflow'
    capabilities: Set[str]  # Supported UAI methods

    def __init__(self):
        if not hasattr(self, 'capabilities'):
            self.capabilities = set()

    def chat(self, msg: Any) -> Any:
        raise NotImplementedError({"error": "capability_not_supported"})

    def stream(self, msg: Any):
        raise NotImplementedError({"error": "capability_not_supported"})

    def run(self, input: Any, **kw) -> Any:
        raise NotImplementedError({"error": "capability_not_supported"})

    def status(self, task_id: Any) -> Any:
        raise NotImplementedError({"error": "capability_not_supported"})

    def results(self, task_id: Any) -> Any:
        raise NotImplementedError({"error": "capability_not_supported"})

    def artifacts(self, task_id: Any) -> Any:
        raise NotImplementedError({"error": "capability_not_supported"})

    def await_prompt(self, task_id: Any) -> Any:
        raise NotImplementedError({"error": "capability_not_supported"})

    def reply(self, task_id: Any, answer: Any) -> Any:
        raise NotImplementedError({"error": "capability_not_supported"})
