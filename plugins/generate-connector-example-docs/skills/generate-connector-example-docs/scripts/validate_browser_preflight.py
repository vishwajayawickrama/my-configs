#!/usr/bin/env python3
"""Validate browser workspace and viewport before connector UI work begins."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from run_lifecycle import matches_workspace_url, read_context, workspace_url, write_context


def validate_preflight(context_path: Path, screenshot: Path, actual_url: str) -> dict:
    context = read_context(context_path)
    expected = context["browser"]["expected_viewport"]
    if not screenshot.is_file():
        raise ValueError(f"Preflight screenshot does not exist: {screenshot}")
    with Image.open(screenshot) as image:
        actual_size = {"width": image.width, "height": image.height}
    expected_url = workspace_url(context)
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "expected_url": expected_url,
        "actual_url": actual_url,
        "expected_viewport": expected,
        "actual_viewport": actual_size,
        "screenshot": str(screenshot.resolve()),
        "workspace_matches": matches_workspace_url(actual_url, context["sample_dir"]),
        "viewport_matches": actual_size == expected,
    }
    context["browser"]["preflight"] = result
    write_context(context_path, context)
    Path(context["run_log_dir"]).joinpath("browser-preflight.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not result["workspace_matches"]:
        raise ValueError("Browser URL does not resolve to this run's exact sample_dir")
    if not result["viewport_matches"]:
        raise ValueError(
            f"Browser viewport is {actual_size['width']}x{actual_size['height']}; "
            f"expected {expected['width']}x{expected['height']}"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--screenshot", required=True, type=Path)
    parser.add_argument("--actual-url", required=True)
    args = parser.parse_args()
    try:
        result = validate_preflight(args.context.resolve(), args.screenshot.resolve(), args.actual_url)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
