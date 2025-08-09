from __future__ import annotations

from datetime import datetime, timedelta

from ...models.run import RunTask
from .run_base import RunAgent


class InputRequiredAgent(RunAgent):
    """Requires user input before proceeding to completion."""

    def __init__(self, post_input_duration_seconds: int = 3) -> None:
        self.duration = post_input_duration_seconds

    def name(self) -> str:
        return "run_input_required"

    def on_create(self, task: RunTask, initial_input: str | None) -> None:
        task.status = "waiting_input"
        task.params["agent"] = self.name()
        if initial_input:
            task.input_buffer.append(initial_input)

    def on_status(self, task: RunTask) -> None:
        if task.status == "running" and task.estimated_completion_time:
            if datetime.utcnow() >= task.estimated_completion_time:
                task.status = "completed"
                last = task.input_buffer[-1] if task.input_buffer else ""
                task.result_text = f"Processed after input: {last}".strip()

    def on_input(self, task: RunTask, text: str) -> None:
        task.input_buffer.append(text)
        # Transition to running and set ETA
        task.status = "running"
        task.estimated_completion_time = datetime.utcnow() + timedelta(seconds=self.duration)

