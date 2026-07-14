#!/usr/bin/env python3
"""Start a code-server process owned by one connector-documentation run."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from run_lifecycle import find_free_port, read_context, write_context, workspace_url


def default_extensions_dir() -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "code-server" / "extensions"


def build_command(context: dict, port: int, user_data_dir: Path) -> list[str]:
    return [
        "code-server",
        "--auth", "none",
        "--bind-addr", f"127.0.0.1:{port}",
        "--user-data-dir", str(user_data_dir),
        "--extensions-dir", str(default_extensions_dir()),
        "--disable-telemetry",
        "--disable-update-check",
        "--ignore-last-opened",
        "--new-window",
        str(Path(context["sample_parent_dir"]).resolve()),
    ]


def wait_until_ready(endpoint: str, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(endpoint, timeout=2) as response:
                if 200 <= response.status < 400:
                    return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"code-server did not become ready within {timeout:g} seconds: {endpoint}")


def start(context_path: Path, port: int | None = None, timeout: float = 30.0) -> dict:
    context = read_context(context_path)
    server = context.setdefault("code_server", {})
    if server.get("started_by_run"):
        raise ValueError("This run already owns a code-server process; run cleanup before restarting it")

    selected_port = port or find_free_port()
    run_log_dir = Path(context["run_log_dir"])
    user_data_dir = run_log_dir / "code-server-data"
    log_path = run_log_dir / "code-server.log"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    command = build_command(context, selected_port, user_data_dir)
    with log_path.open("ab") as log_file:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    endpoint = f"http://127.0.0.1:{selected_port}"
    server.update({
        "endpoint": endpoint,
        "port": selected_port,
        "process_group": process.pid,
        "pid": process.pid,
        "started_by_run": True,
        "user_data_dir": str(user_data_dir.resolve()),
        "workspace": str(Path(context["sample_parent_dir"]).resolve()),
        "log_path": str(log_path.resolve()),
    })
    write_context(context_path, context)
    try:
        wait_until_ready(endpoint, timeout)
    except Exception:
        # Leave the ownership record intact so cleanup_run.py can safely stop it.
        raise
    return {"endpoint": endpoint, "workspace_url": workspace_url(context), "pid": process.pid, "port": selected_port}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--port", type=int, help="Use this free loopback port instead of selecting one")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    try:
        if args.port is not None and not 1 <= args.port <= 65535:
            raise ValueError("--port must be in the range 1..65535")
        result = start(args.context.resolve(), args.port, args.timeout)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(__import__("json").dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
