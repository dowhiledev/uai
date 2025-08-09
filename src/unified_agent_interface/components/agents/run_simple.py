from __future__ import annotations

from datetime import datetime, timedelta

from ...models.run import RunTask
from .run_base import RunAgent


class SimpleLongRunningAgent(RunAgent):
    """Completes automatically after a short duration."""

    def __init__(self, duration_seconds: int = 3) -> None:
        self.duration = duration_seconds

    def name(self) -> str:
        return "run_simple"

    def on_create(self, task: RunTask, initial_input: str | None) -> None:
        task.status = "running"
        task.estimated_completion_time = datetime.utcnow() + timedelta(seconds=self.duration)
        task.params["agent"] = self.name()

    def on_status(self, task: RunTask) -> None:
        if task.status == "running" and task.estimated_completion_time:
            if datetime.utcnow() >= task.estimated_completion_time:
                task.status = "completed"
                task.result_text = (task.input_buffer[-1] if task.input_buffer else "Done.")

    def on_input(self, task: RunTask, text: str) -> None:
        # No special handling; just append input
        task.input_buffer.append(text)

