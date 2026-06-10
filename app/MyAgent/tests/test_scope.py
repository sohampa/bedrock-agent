"""Policy gate: code review scope (no Bedrock required)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from review.payload import parse_review_payload  # noqa: E402
from review.scope import is_in_scope  # noqa: E402


def test_denies_hello():
    data = parse_review_payload({"prompt": "Hello, how are you?"})
    allowed, _ = is_in_scope(data)
    assert not allowed


def test_allows_style_and_readability_review():
    data = parse_review_payload({"prompt": "Review for readability and naming"})
    allowed, _ = is_in_scope(data)
    assert allowed


def test_allows_best_practices_review():
    data = parse_review_payload({"prompt": "Review this code for best practices and error handling"})
    allowed, _ = is_in_scope(data)
    assert allowed


def test_allows_security_with_diff():
    data = parse_review_payload(
        {
            "prompt": "Review for security vulnerabilities",
            "mode": "ci",
            "diff": "diff --git a/x.py b/x.py\n+eval(user_input)",
        }
    )
    allowed, _ = is_in_scope(data)
    assert allowed


def test_allows_security_prompt():
    data = parse_review_payload(
        {"prompt": "Review this PR for security issues and SQL injection"}
    )
    allowed, _ = is_in_scope(data)
    assert allowed
