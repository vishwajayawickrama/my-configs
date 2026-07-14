"""Shared helpers for the isolated code-server and browser-run lifecycle."""

from __future__ import annotations

import json
import socket
import urllib.parse
from pathlib import Path


def read_context(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_context(path: Path, context: dict) -> None:
    path.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def workspace_url(context: dict) -> str:
    endpoint = context.get("code_server", {}).get("endpoint")
    if not endpoint:
        raise ValueError("code-server endpoint is not recorded in the run context")
    folder = urllib.parse.quote(str(Path(context["sample_dir"]).resolve()), safe="")
    return f"{endpoint.rstrip('/')}/?folder={folder}"


def matches_workspace_url(url: str, expected_sample_dir: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    folder = urllib.parse.parse_qs(parsed.query).get("folder", [None])[0]
    if folder is None:
        return False
    try:
        return Path(urllib.parse.unquote(folder)).resolve() == Path(expected_sample_dir).resolve()
    except OSError:
        return False
