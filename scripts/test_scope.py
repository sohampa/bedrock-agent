#!/usr/bin/env python3
"""Quick local test for security scope guard (no AWS/Bedrock required)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app" / "MyAgent"
sys.path.insert(0, str(ROOT))

from review.payload import parse_review_payload  # noqa: E402
from review.scope import is_in_scope  # noqa: E402


def check(label: str, raw: dict, expect_allow: bool) -> bool:
    data = parse_review_payload(raw)
    allowed, denial = is_in_scope(data)
    ok = allowed == expect_allow
    status = "PASS" if ok else "FAIL"
    outcome = "ALLOW" if allowed else "DENY"
    print(f"[{status}] {label} -> {outcome}")
    if not ok:
        print(f"       expected {'ALLOW' if expect_allow else 'DENY'}")
    if denial and not allowed:
        print(f"       message starts: {denial[:80]}...")
    return ok


def main() -> int:
    tests = [
        ("hello denied", {"prompt": "Hello, how are you?"}, False),
        ("style-only denied", {"prompt": "Review for readability only"}, False),
        (
            "security + diff allowed",
            {
                "prompt": "Review for security vulnerabilities",
                "mode": "ci",
                "diff": "diff --git a/x.py b/x.py\n+password = 'secret'",
            },
            True,
        ),
        (
            "security prompt allowed",
            {"prompt": "Review this PR for security issues and injection risks"},
            True,
        ),
    ]
    passed = sum(1 for t in tests if check(*t))
    print(f"\n{passed}/{len(tests)} scope checks passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
