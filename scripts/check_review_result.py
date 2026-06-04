#!/usr/bin/env python3
"""Parse agentcore invoke --json output and exit 1 if critical findings > 0."""

import json
import re
import sys


def extract_meta(text: str) -> dict | None:
    match = re.search(
        r"<!--\s*REVIEW_META\s*(\{[^}]+\})\s*-->", text, re.IGNORECASE
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "review-result.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    text = ""
    if isinstance(data, dict):
        text = data.get("response", "") or data.get("text", "") or ""
        if isinstance(text, dict):
            text = text.get("text", json.dumps(text))

    meta = extract_meta(text) if isinstance(text, str) else None
    critical = int(meta.get("critical", 0)) if meta else 0

    if critical > 0:
        print(f"Code review failed: {critical} critical finding(s).")
        sys.exit(1)

    if meta is None:
        print(
            "Warning: REVIEW_META footer not found; skipping critical gate. "
            "Ensure the agent runs in CI mode."
        )
    else:
        print(f"Code review passed (critical={critical}).")
    sys.exit(0)


if __name__ == "__main__":
    main()
