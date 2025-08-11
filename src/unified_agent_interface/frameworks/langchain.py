from __future__ import annotations

from typing import Any

from .base import RuntimeAdapter


class LangChainAdapter(RuntimeAdapter):
    def name(self) -> str:
        return "langchain"

    def supports_chat(self) -> bool:
        return True

    def execute(
        self,
        entrypoint_obj: Any,
        *,
        task_id: str,
        initial_payload: Any | None,
        config_dir: str | None = None,
    ) -> str:
        # Determine how to send inputs to the chain/runnable
        inputs: Any
        if isinstance(initial_payload, dict):
            inputs = initial_payload
        elif isinstance(initial_payload, str):
            # Common convention: map string input to {"text": "..."}
            inputs = {"text": initial_payload}
        else:
            inputs = {}

        # Prefer LangChain Runnable protocol: .invoke
        if hasattr(entrypoint_obj, "invoke") and callable(getattr(entrypoint_obj, "invoke")):
            result = entrypoint_obj.invoke(inputs)
        elif hasattr(entrypoint_obj, "run") and callable(getattr(entrypoint_obj, "run")):
            # Legacy LLMChain interface
            try:
                result = entrypoint_obj.run(inputs)
            except TypeError:
                result = entrypoint_obj.run(initial_payload)
        else:
            raise TypeError("Unsupported LangChain entrypoint: expected a Runnable or LLMChain")

        return self._normalize_result(result)

    def chat_respond(
        self,
        entrypoint_obj: Any,
        *,
        session_id: str,
        user_input: str,
        state: dict | None,
        config_dir: str | None = None,
    ) -> str:
        # Map user input to expected fields; include state if provided
        inputs: Any
        base = state.copy() if isinstance(state, dict) else {}
        base.setdefault("text", user_input)
        inputs = base

        if hasattr(entrypoint_obj, "invoke") and callable(getattr(entrypoint_obj, "invoke")):
            result = entrypoint_obj.invoke(inputs)
        elif hasattr(entrypoint_obj, "run") and callable(getattr(entrypoint_obj, "run")):
            try:
                result = entrypoint_obj.run(inputs)
            except TypeError:
                result = entrypoint_obj.run(user_input)
        else:
            raise TypeError("Unsupported LangChain entrypoint for chat")

        return self._normalize_result(result)

    def _normalize_result(self, result: Any) -> str:
        # Normalize result to string
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
