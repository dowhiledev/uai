from __future__ import annotations

from typing import Protocol, Tuple

from ...models.chat import Artifact, Message


class Agent(Protocol):
    def respond(self, session_id: str, state: dict, user_input: str) -> Tuple[dict, list[Artifact], Message | None]:
        """Generate next response for a session given state and user input."""
        ...
