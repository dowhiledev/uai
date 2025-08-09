from __future__ import annotations

import uuid
from typing import Tuple

from ...models.chat import Artifact, Message


class MultiTurnChatAgent:
    """A simple multi-turn chat agent that tracks turns in state.

    - Increments a `turn` counter in the provided state dict.
    - Echos back user input with the turn number.
    - If user mentions the word "artifact", emits a mock artifact.
    """

    def respond(self, state: dict, user_input: str) -> Tuple[dict, list[Artifact], Message | None]:
        turn = int(state.get("turn", 0)) + 1
        state["turn"] = turn
        reply = Message(id=str(uuid.uuid4()), role="assistant", content=f"[turn {turn}] You said: {user_input}")

        artifacts: list[Artifact] = []
        if "artifact" in (user_input or "").lower():
            artifacts.append(
                Artifact(id=str(uuid.uuid4()), type="note", name=f"artifact-turn-{turn}", uri=None, metadata={"turn": turn})
            )

        return state, artifacts, reply

