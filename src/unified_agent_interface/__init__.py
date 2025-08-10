from .app import get_app  # re-export app factory


# Typer CLI entrypoint defined in pyproject as `uai`.
def cli() -> None:  # pragma: no cover
    import json
    import typing as t
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

    def _http_post(url: str, path: str, json_body: dict) -> dict:
        import httpx  # lazy import
        r = httpx.post(url.rstrip("/") + path, json=json_body, timeout=60)
        r.raise_for_status()
        return r.json() if r.text else {}

    def _http_get(url: str, path: str) -> dict:
        import httpx  # lazy import
        r = httpx.get(url.rstrip("/") + path, timeout=60)
        r.raise_for_status()
        return r.json() if r.text else {}

    def _print(data: t.Any) -> None:
        try:
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception:
            typer.echo(str(data))

    run_app = typer.Typer(help="Interact with run tasks")
    chat_app = typer.Typer(help="Interact with chat sessions")

    @run_app.command("create")
    def run_create(
        input: str = typer.Option(None, "--input", help="Initial run input"),
        url: str = typer.Option("http://localhost:8000", "--url", help="Base server URL"),
        param: t.List[str] = typer.Option(None, "--param", help="Extra param key=value", show_default=False),
    ) -> None:
        params: dict[str, t.Any] = {}
        for p in param or []:
            if "=" in p:
                k, v = p.split("=", 1)
                params[k] = v
        payload = {"input": input, "params": params or None}
        data = _http_post(url, "/run/", payload)
        _print(data)

    @run_app.command("status")
    def run_status(
        task_id: str = typer.Argument(..., help="Task ID"),
        url: str = typer.Option("http://localhost:8000", "--url", help="Base server URL"),
    ) -> None:
        data = _http_get(url, f"/run/{task_id}")
        _print(data)

    @run_app.command("input")
    def run_input(
        task_id: str = typer.Argument(..., help="Task ID"),
        text: str = typer.Option(..., "--text", help="Input text"),
        url: str = typer.Option("http://localhost:8000", "--url", help="Base server URL"),
    ) -> None:
        data = _http_post(url, f"/run/{task_id}/input", {"input": text})
        _print(data)

    @run_app.command("logs")
    def run_logs(
        task_id: str = typer.Argument(..., help="Task ID"),
        message: str = typer.Option(..., "--message", help="Log message"),
        level: str = typer.Option("INFO", "--level", help="Log level"),
        url: str = typer.Option("http://localhost:8000", "--url", help="Base server URL"),
    ) -> None:
        data = _http_post(url, f"/run/{task_id}/logs", {"level": level, "message": message})
        _print(data)

    @chat_app.command("create")
    def chat_create(
        url: str = typer.Option("http://localhost:8000", "--url", help="Base server URL"),
    ) -> None:
        data = _http_post(url, "/chat/", {})
        _print(data)

    @chat_app.command("send")
    def chat_send(
        session_id: str = typer.Argument(..., help="Chat session ID"),
        text: str = typer.Option(..., "--text", help="User message"),
        url: str = typer.Option("http://localhost:8000", "--url", help="Base server URL"),
    ) -> None:
        data = _http_post(url, f"/chat/{session_id}", {"user_input": text})
        _print(data)

    @chat_app.command("messages")
    def chat_messages(
        session_id: str = typer.Argument(..., help="Chat session ID"),
        url: str = typer.Option("http://localhost:8000", "--url", help="Base server URL"),
    ) -> None:
        data = _http_get(url, f"/chat/{session_id}/messages")
        _print(data)

    app.add_typer(run_app, name="run")
    app.add_typer(chat_app, name="chat")

    app()
