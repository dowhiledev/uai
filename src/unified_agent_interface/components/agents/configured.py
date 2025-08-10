from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Dict, Optional

from ...config import AgentConfig, import_entrypoint
from ...models.run import RunTask
from .run_base import RunAgent


class ConfiguredRunAgent(RunAgent):
    """RunAgent that uses kosmos agent config to dispatch to a specific runtime.

    Supported runtimes:
    - "crewai": entrypoint should be a Crew object exposing `.kickoff(inputs=...)`
    - "callable": entrypoint is a Python callable; called with `(inputs: dict)`
    """

    def __init__(self, cfg: AgentConfig, eta_seconds: int = 5) -> None:
        self.cfg = cfg
        self._eta_seconds = eta_seconds
        self._threads: Dict[str, threading.Thread] = {}

    def name(self) -> str:  # Reflect configured runtime
        return f"configured:{self.cfg.runtime}"

    def _start_thread(self, task: RunTask, target):
        t = threading.Thread(target=target, daemon=True)
        self._threads[task.id] = t
        t.start()

    def on_create(self, task: RunTask, initial_input: str | None) -> None:
        task.status = "running"
        task.params["agent"] = self.name()
        task.estimated_completion_time = datetime.utcnow() + timedelta(seconds=self._eta_seconds)

        runtime = self.cfg.runtime.lower()
        # Try to import entrypoint early; if it fails, mark task as failed gracefully.
        try:
            # Optionally load examples/.env if present (best effort)
            try:
                from dotenv import load_dotenv  # type: ignore
                from pathlib import Path
                import os
                env_path = Path(os.getcwd()) / "examples" / ".env"
                if env_path.exists():
                    load_dotenv(env_path)
            except Exception:
                pass

            entry_obj, _, _ = import_entrypoint(self.cfg.entrypoint)
        except Exception as e:
            task.status = "failed"
            task.result_text = f"Import error: {e}"
            task.estimated_completion_time = None
            return

        if runtime == "crewai":
            # Expect a Crew-like object with kickoff(inputs=...)
            inputs: Optional[dict] = {"topic": (initial_input or "").strip()}

            def runner():
                try:
                    result = entry_obj.kickoff(inputs=inputs)
                    task.result_text = str(result)
                    task.status = "completed"
                except Exception as e:  # pragma: no cover - integration path
                    task.status = "failed"
                    task.result_text = f"CrewAI error: {e}"
                finally:
                    task.estimated_completion_time = None

            self._start_thread(task, runner)

        elif runtime == "callable":
            # Call arbitrary callable; pass dict with 'input' and 'params'
            if not callable(entry_obj):
                task.status = "failed"
                task.result_text = "Configured entrypoint is not callable"
                task.estimated_completion_time = None
                return

            def runner():
                try:
                    payload = {"input": initial_input, "params": dict(task.params)}
                    result = entry_obj(payload)
                    task.result_text = str(result) if result is not None else ""
                    task.status = "completed"
                except Exception as e:
                    task.status = "failed"
                    task.result_text = f"Callable error: {e}"
                finally:
                    task.estimated_completion_time = None

            self._start_thread(task, runner)

        else:
            task.status = "failed"
            task.result_text = f"Unsupported runtime: {self.cfg.runtime}"
            task.estimated_completion_time = None

    def on_status(self, task: RunTask) -> None:
        t = self._threads.get(task.id)
        if t and not t.is_alive() and task.status == "running":
            task.status = "completed"
            task.estimated_completion_time = None

    def on_input(self, task: RunTask, text: str) -> None:
        task.input_buffer.append(text)
