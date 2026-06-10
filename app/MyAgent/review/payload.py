import json
from typing import Any


def parse_review_payload(payload: Any) -> dict[str, Any]:
    """Normalize invoke payload from HTTP body or agentcore invoke prompt."""
    if not isinstance(payload, dict):
        return {
            "prompt": str(payload)
            if payload
            else "Review the provided changes for security issues."
        }

    data = dict(payload)

    prompt = data.get("prompt")
    if isinstance(prompt, str) and prompt.strip().startswith("{"):
        try:
            embedded = json.loads(prompt)
            if isinstance(embedded, dict):
                data = {**embedded, **{k: v for k, v in data.items() if k != "prompt"}}
                if "prompt" not in embedded and prompt:
                    default_prompt = embedded.get("prompt", "Review the provided changes.")
                    data.setdefault("prompt", default_prompt)
        except json.JSONDecodeError:
            pass

    data.setdefault("prompt", "Review the provided changes for security issues.")
    data.setdefault("mode", _infer_mode(data))
    return data


def _infer_mode(data: dict[str, Any]) -> str:
    if data.get("mode"):
        return str(data["mode"])
    if data.get("pr_number") and data.get("owner") and data.get("repo"):
        return "pr"
    if data.get("diff") or data.get("files"):
        return "ci"
    return "chat"


def build_user_message(data: dict[str, Any]) -> str:
    """Build the user message sent to the model."""
    parts: list[str] = [str(data.get("prompt", "Review the provided changes."))]

    mode = data.get("mode", "chat")
    parts.append(f"\n\n**Mode:** {mode}")

    if data.get("focus"):
        focus = data["focus"]
        if isinstance(focus, list):
            parts.append(f"**Focus areas:** {', '.join(str(f) for f in focus)}")
        else:
            parts.append(f"**Focus areas:** {focus}")

    owner, repo, pr_number = data.get("owner"), data.get("repo"), data.get("pr_number")
    if owner and repo and pr_number:
        parts.append(f"\n**GitHub PR:** {owner}/{repo}#{pr_number}")
        if data.get("post_comment"):
            parts.append(
                "**Action:** After review, call `post_github_pr_review_comment` "
                "with the full review body."
            )
        else:
            parts.append(
                "**Action:** Use `fetch_github_pr_diff` if you need the patch; "
                "do not post to GitHub unless asked."
            )

    diff = data.get("diff")
    if diff:
        parts.append(f"\n\n## Diff\n```diff\n{diff}\n```")

    files = data.get("files")
    if isinstance(files, list):
        for item in files:
            if not isinstance(item, dict):
                continue
            path = item.get("path", "unknown")
            content = item.get("content", "")
            parts.append(f"\n\n## File: `{path}`\n```\n{content}\n```")

    if mode == "ci":
        parts.append(
            "\n\n**CI:** End with the REVIEW_META footer. Mark build-blocking issues as Critical."
        )

    return "".join(parts)
