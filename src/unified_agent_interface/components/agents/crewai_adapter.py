from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Dict, Optional

from ...models.run import RunTask
from .run_base import RunAgent


class CrewAIRunAgent(RunAgent):
    """Adapter for running a CrewAI Crew via a Python module.

    Params (in `RunTask.params` when creating the task):
    - agent: "crewai"
    - crewai_module: Python module path exposing a `crew` object (default: "examples.crewai_example")
    - crewai_inputs: dict passed to `crew.kickoff(inputs=...)` (default: {"topic": initial_input or ""})

    This adapter lazily imports the target module to avoid hard dependency unless selected.
    It runs the kickoff in a background thread and updates the RunTask when complete.
    """

    def __init__(self, eta_seconds: int = 10) -> None:
        self._eta_seconds = eta_seconds
        self._threads: Dict[str, threading.Thread] = {}

    def name(self) -> str:
        return "crewai"

    def on_create(self, task: RunTask, initial_input: str | None) -> None:
        task.status = "running"
        task.params["agent"] = self.name()
        # optimistic ETA until we know
        task.estimated_completion_time = datetime.utcnow() + timedelta(seconds=self._eta_seconds)

        module_path: str = task.params.get("crewai_module", "examples.crewai_example")
        inputs: Optional[dict] = task.params.get("crewai_inputs")
        if inputs is None:
            inputs = {"topic": (initial_input or "").strip()}

        def runner():
            try:
                import importlib
                # Load .env in examples if present
                try:
                    from dotenv import load_dotenv
                    import os
                    from pathlib import Path

                    env_path = Path(os.getcwd()) / "examples" / ".env"
                    if env_path.exists():
                        load_dotenv(env_path)  # do not override existing env
                except Exception:
                    # dotenv is optional; ignore if missing
                    pass

                mod = importlib.import_module(module_path)
                crew = getattr(mod, "crew", None)
                if crew is None:
                    raise RuntimeError(f"Module '{module_path}' does not expose a 'crew' instance")

                result = crew.kickoff(inputs=inputs)
                task.result_text = str(result)
                task.status = "completed"
            except Exception as e:  # pragma: no cover - integration error path
                task.status = "failed"
                task.result_text = f"CrewAI error: {e}"
            finally:
                task.estimated_completion_time = None

        t = threading.Thread(target=runner, daemon=True)
        self._threads[task.id] = t
        t.start()

    def on_status(self, task: RunTask) -> None:
        t = self._threads.get(task.id)
        if t and not t.is_alive() and task.status == "running":
            # Thread finished but status not updated (unlikely), mark as completed
            task.status = "completed"
            task.estimated_completion_time = None

    def on_input(self, task: RunTask, text: str) -> None:
        # CrewAI flow doesn't support mid-run input via this adapter; just record it.
        task.input_buffer.append(text)
