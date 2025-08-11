from __future__ import annotations

import importlib
import sys
from typing import Any, Dict, Tuple, List

from .base import Agent
from ...config import AgentConfig, import_entrypoint
from ...models.chat import Artifact, Message
from ...frameworks import get_adapter


class ConfiguredChatAgent(Agent):
    """Chat agent using kosmos.toml runtime.

    For LangChain, maintains a per-session chain instance (separate memory) and
    executes synchronously, returning the assistant reply text as a Message.
    """

    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg
        self._instances: Dict[str, Any] = {}

    def runtime(self) -> str:
        return self.cfg.runtime

    def _langchain_ensure_instance(self, session_id: str) -> Any:
        if session_id in self._instances:
            return self._instances[session_id]

        # Load a fresh instance for this session. We try to reload the module
        # to re-execute module-level construction (e.g., memory/chain objects).
        obj, mod_name, attr_path = import_entrypoint(self.cfg.entrypoint, base_dir=self.cfg.base_dir)
        try:
            if mod_name in sys.modules:
                m = sys.modules[mod_name]
                importlib.reload(m)
                # Re-resolve attribute after reload
                for part in attr_path.split('.'):
                    obj = getattr(m, part)
        except Exception:
            # Fallback to the initially imported object
            pass

        self._instances[session_id] = obj
        return obj

    def _normalize_langchain_result(self, result: Any) -> str:
        try:
            if hasattr(result, "content"):
                return str(getattr(result, "content"))
            if isinstance(result, dict):
                for key in ("text", "output_text", "output", "result"):
                    if key in result:
                        return str(result[key])
            return "" if result is None else str(result)
        except Exception:
            return str(result)

    def respond(self, session_id: str, state: dict, user_input: str) -> Tuple[dict, List[Artifact], Message | None]:
        rt = (self.cfg.runtime or "").lower()
        adapter = get_adapter(rt)
        if not adapter.supports_chat():
            raise NotImplementedError(f"Chat not implemented for runtime: {self.cfg.runtime}")

        # For frameworks like LangChain, create or reuse a per-session entrypoint instance
        inst = self._langchain_ensure_instance(session_id) if rt == "langchain" else import_entrypoint(self.cfg.entrypoint, base_dir=self.cfg.base_dir)[0]
        text = adapter.chat_respond(
            inst,
            session_id=session_id,
            user_input=user_input,
            state=state or {},
            config_dir=self.cfg.base_dir,
        )
        reply = Message(role="assistant", content=text)
        return state or {}, [], reply
