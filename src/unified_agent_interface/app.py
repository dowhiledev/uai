from fastapi import FastAPI

from .api.router import api_router
from .components.storage.memory import InMemoryStorage
from .config import load_kosmos_agent_config
from .components.agents.configured import ConfiguredRunAgent


def get_app() -> FastAPI:
    app = FastAPI(title="Unified Agent Interface", version="0.1.0")

    # Initialize in-memory storage (placeholder; swap with Postgres/Redis later)
    app.state.storage = InMemoryStorage()

    # Load kosmos agent configuration and prepare run agent
    cfg = load_kosmos_agent_config()
    app.state.run_agent = ConfiguredRunAgent(cfg)

    # Mount API
    app.include_router(api_router)

    return app
