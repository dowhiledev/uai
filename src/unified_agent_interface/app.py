from fastapi import FastAPI

from .api.router import api_router
from .components.storage.memory import InMemoryStorage


def get_app() -> FastAPI:
    app = FastAPI(title="Unified Agent Interface", version="0.1.0")

    # Initialize in-memory storage (placeholder; swap with Postgres/Redis later)
    app.state.storage = InMemoryStorage()

    # Mount API
    app.include_router(api_router)

    return app

