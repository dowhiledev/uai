from __future__ import annotations

import uuid
from typing import Tuple

from ...models.chat import Artifact, Message


class EchoAgent:
    def respond(self, state: dict, user_input: str) -> Tuple[dict, list[Artifact], Message | None]:
        reply = Message(id=str(uuid.uuid4()), role="assistant", content=f"Echo: {user_input}")
        return state, [], reply

