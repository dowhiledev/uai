from .app import get_app  # re-export app factory

# Typer CLI entrypoint defined in pyproject as `uai`.
def cli() -> None:  # pragma: no cover
    import typer
    import uvicorn

    app = typer.Typer(help="Unified Agent Interface (UAI) CLI")

    @app.command()
    def serve(
        host: str = "0.0.0.0",
        port: int = 8000,
        reload: bool = True,
    ) -> None:
        """Run the UAI FastAPI server."""

        uvicorn.run(
            "unified_agent_interface.app:get_app",
            factory=True,
            host=host,
            port=port,
            reload=reload,
        )

    app()
