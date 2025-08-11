from __future__ import annotations

from typing import Any

from .base import RuntimeAdapter


class CallableAdapter(RuntimeAdapter):
    def name(self) -> str:
        return "callable"

    def execute(
        self,
        entrypoint_obj: Any,
        *,
        task_id: str,
        initial_payload: Any | None,
        config_dir: str | None = None,
    ) -> str:
        if not callable(entrypoint_obj):
            raise TypeError("entrypoint is not callable")
        if isinstance(initial_payload, dict):
            try:
                result = entrypoint_obj(**initial_payload)
            except TypeError:
                result = entrypoint_obj(initial_payload)
        else:
            result = entrypoint_obj({"input": initial_payload, "params": {}})
        return "" if result is None else str(result)

