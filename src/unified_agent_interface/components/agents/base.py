from __future__ import annotations

from typing import Protocol, Tuple

from ...models.chat import Artifact, Message


class Agent(Protocol):
    def respond(self, state: dict, user_input: str) -> Tuple[dict, list[Artifact], Message | None]:
        """Generate next response given state and user input."""
        ...

