#!/usr/bin/env python3
"""Append Central examples, crop screenshots once, validate, and write run.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from crop_screenshots import crop_directory
from validate_output import validate


def extract_examples(readme: str) -> Optional[str]:
    lines = readme.splitlines()
    start = None
    level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+examples?\s*$", line.strip(), re.I)
        if match:
            start = index + 1
            level = len(match.group(1))
            break
    if start is None:
        return None
    body: list[str] = []
    for line in lines[start:]:
        heading = re.match(r"^(#{1,6})\s+", line)
        if heading and len(heading.group(1)) <= level:
            break
        body.append(line)
    value = "\n".join(body).strip()
    return value or None


def append_examples(doc_path: Path, metadata_path: Path) -> bool:
    text = doc_path.read_text(encoding="utf-8")
    if re.search(r"^## More code examples\s*$", text, re.M):
        return False
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    readme = metadata.get("readme")
    examples = extract_examples(readme) if isinstance(readme, str) else None
    if not examples:
        return False
    doc_path.write_text(text.rstrip() + "\n\n## More code examples\n\n" + examples + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--skip-crop", action="store_true", help="Keep original screenshots")
    args = parser.parse_args()
    try:
        context = json.loads(args.context.read_text(encoding="utf-8"))
        doc_path = Path(context["doc_path"])
        run_json_path = Path(context["run_log_dir"]) / "run.json"
        previous = json.loads(run_json_path.read_text(encoding="utf-8")) if run_json_path.exists() else {}
        examples_added = append_examples(doc_path, Path(context["metadata_path"]))
        already_cropped = bool(previous.get("screenshots_cropped"))
        if not args.skip_crop and not already_cropped:
            crop_directory(Path(context["screenshots_dir"]))
        errors = validate(context)
        result = {
            **context,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "examples_added": bool(previous.get("examples_added")) or examples_added,
            "screenshots_cropped": already_cropped or not args.skip_crop,
            "validation": {"status": "passed" if not errors else "failed", "errors": errors},
        }
        run_json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, KeyError) as exc:
        print(f"[ERROR] Finalization failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        return 1
    print(f"Finalized and validated: {context['run_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
