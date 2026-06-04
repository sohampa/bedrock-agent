#!/usr/bin/env python3
"""Build JSON payload for agentcore invoke --prompt-file (stored as prompt string)."""

import argparse
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["ci", "pr", "chat"], default="ci")
    parser.add_argument(
        "--prompt",
        default="Review this change for security vulnerabilities and unsafe patterns.",
    )
    parser.add_argument("--owner", default="")
    parser.add_argument("--repo", default="")
    parser.add_argument("--pr-number", type=int, default=0)
    parser.add_argument("--diff-file", default="")
    parser.add_argument("--post-comment", action="store_true")
    parser.add_argument("--focus", action="append", default=[])
    args = parser.parse_args()

    diff = ""
    if args.diff_file == "-":
        diff = sys.stdin.read()
    elif args.diff_file:
        with open(args.diff_file, encoding="utf-8") as f:
            diff = f.read()

    payload: dict = {
        "prompt": args.prompt,
        "mode": args.mode,
        "post_comment": args.post_comment,
    }
    if args.owner:
        payload["owner"] = args.owner
    if args.repo:
        payload["repo"] = args.repo
    if args.pr_number:
        payload["pr_number"] = args.pr_number
    if diff:
        payload["diff"] = diff
    if args.focus:
        payload["focus"] = args.focus

    # agentcore invoke --prompt-file sends file contents as the "prompt" field
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
