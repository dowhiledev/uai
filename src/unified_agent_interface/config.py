from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple


@dataclass
class AgentConfig:
    runtime: str
    entrypoint: str
    raw: dict


def _read_toml(path: Path) -> dict:
    try:  # Python >=3.11
        import tomllib  # type: ignore
    except Exception:  # pragma: no cover - fallback if needed
        import tomli as tomllib  # type: ignore
    with path.open('rb') as f:
        return tomllib.load(f)


def load_kosmos_agent_config(path: Optional[str] = None) -> AgentConfig:
    """Load kosmos.toml and return AgentConfig.

    Order of resolution:
    - explicit `path` if provided
    - env var `KOSMOS_TOML`
    - `./kosmos.toml` if exists
    - `./examples/kosmos.toml` if exists
    """
    candidates = []
    if path:
        candidates.append(Path(path))
    env_path = os.getenv('KOSMOS_TOML')
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path('kosmos.toml'))
    candidates.append(Path('examples') / 'kosmos.toml')

    chosen: Optional[Path] = None
    for p in candidates:
        if p and p.exists():
            chosen = p
            break
    if not chosen:
        raise FileNotFoundError('kosmos.toml not found in expected locations')

    data = _read_toml(chosen)
    agent_section = data.get('agent') or {}
    runtime = agent_section.get('runtime')
    entrypoint = agent_section.get('entrypoint')
    if not runtime or not entrypoint:
        raise ValueError('agent.runtime and agent.entrypoint must be set in kosmos.toml')
    return AgentConfig(runtime=str(runtime), entrypoint=str(entrypoint), raw=agent_section)


def import_entrypoint(entrypoint: str) -> Tuple[Any, str, str]:
    """Import `module:attr` and return (obj, module_name, attr_name)."""
    if ':' not in entrypoint:
        raise ValueError("entrypoint must be in 'module:attr' format")
    mod_name, attr_path = entrypoint.split(':', 1)
    try:
        mod = importlib.import_module(mod_name)
    except ModuleNotFoundError:
        # Try file-based import relative to CWD, e.g., examples/foo.py
        from importlib.util import spec_from_file_location, module_from_spec
        candidate = Path(mod_name.replace('.', os.sep) + '.py')
        if not candidate.exists():
            raise
        spec = spec_from_file_location(mod_name, candidate)
        if spec is None or spec.loader is None:
            raise
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    obj = mod
    for part in attr_path.split('.'):
        obj = getattr(obj, part)
    return obj, mod_name, attr_path
