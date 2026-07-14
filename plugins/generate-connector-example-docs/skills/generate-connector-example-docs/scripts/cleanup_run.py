#!/usr/bin/env python3
"""Stop code-server owned by a connector-documentation run and record cleanup."""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

from run_lifecycle import read_context, write_context


def cleanup(context_path: Path, status: str, browser_closed: bool = False) -> dict:
    context = read_context(context_path)
    server = context.setdefault("code_server", {})
    result = {"status": status, "stopped": False, "reason": "not-owned"}
    group = server.get("process_group")
    if server.get("started_by_run") and isinstance(group, int) and group > 0:
        try:
            os.killpg(group, signal.SIGTERM)
            result.update({"stopped": True, "reason": "terminated", "process_group": group})
        except ProcessLookupError:
            result.update({"stopped": True, "reason": "already-exited", "process_group": group})
        except PermissionError as exc:
            result.update({"reason": f"permission-denied: {exc}", "process_group": group})

    result["cleaned_at"] = datetime.now(timezone.utc).isoformat()
    context["cleanup"] = result
    if browser_closed:
        context.setdefault("browser", {})["closed_at"] = result["cleaned_at"]
    server["started_by_run"] = False
    write_context(context_path, context)
    Path(context["run_log_dir"]).joinpath("cleanup.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--status", required=True, choices=("completed", "failed", "partial"))
    parser.add_argument("--browser-closed", action="store_true", help="Record that browser_close succeeded first")
    args = parser.parse_args()
    try:
        print(json.dumps(cleanup(args.context.resolve(), args.status, args.browser_closed), indent=2, sort_keys=True))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
