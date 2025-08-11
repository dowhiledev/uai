from __future__ import annotations

from typing import Any, Protocol


class RuntimeAdapter(Protocol):
    def name(self) -> str: ...

    def execute(
        self,
        entrypoint_obj: Any,
        *,
        task_id: str,
        initial_payload: Any | None,
        config_dir: str | None = None,
    ) -> str:
        """Run the framework using the given entrypoint and return result text.

        Implementations should raise exceptions on failure; callers capture and report.
        """
        ...

