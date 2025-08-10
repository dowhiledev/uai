from __future__ import annotations

from typing import Dict

from .base import Agent
from .echo import EchoAgent
from .chat_multi import MultiTurnChatAgent
from .run_base import RunAgent
from .run_simple import SimpleLongRunningAgent
from .run_input_required import InputRequiredAgent
from .crewai_adapter import CrewAIRunAgent


_chat_agents: Dict[str, Agent] = {
    "echo": EchoAgent(),
    "chat_multi": MultiTurnChatAgent(),
}

_run_agents: Dict[str, RunAgent] = {
    "run_simple": SimpleLongRunningAgent(),
    "run_input_required": InputRequiredAgent(),
    "crewai": CrewAIRunAgent(),
}


def get_chat_agent(name: str) -> Agent:
    return _chat_agents.get(name, _chat_agents["echo"])  # default to echo


def get_run_agent(name: str) -> RunAgent:
    return _run_agents.get(name, _run_agents["run_simple"])  # default to simple
