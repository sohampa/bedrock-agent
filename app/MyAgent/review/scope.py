import re
from typing import Any

DENIAL_MESSAGE = """I'm a **code review** agent focused on **security and developer best practices**.

I can review diffs and pull requests for vulnerabilities, auth issues, secrets exposure, injection risks, error handling, testing gaps, maintainability, naming, structure, and related quality concerns.

I can't help with general chat, trivia, or tasks unrelated to reviewing code.

**To get a review, send:**
- `mode`: `ci` or `pr` with a `diff`, or GitHub `owner` / `repo` / `pr_number`
- A prompt describing what to review (e.g. "Review this change for security and best practices")
"""

# Structured review requests (CI / PR / code review intent).
_REVIEW_INTENT = re.compile(
    r"\b("
    r"review|code\s*review|pull\s*request|pr\s*review|audit|scan|analyze|analyse|"
    r"inspect|feedback|best\s+practices?|code\s+quality|maintainability|"
    r"refactor|improve(?:ment)?|look\s+at|check\s+(?:this|my|the)\s+(?:code|change|pr|diff)"
    r")\b",
    re.IGNORECASE,
)

_SECURITY_TOPIC = re.compile(
    r"\b("
    r"security|secure\s+cod|vulnerabilit|owasp|threat|exploit|cve|cwe|"
    r"injection|xss|csrf|ssrf|sqli|secret|credential|password|token|auth[nz]?|"
    r"encrypt|decrypt|tls|ssl|saniti[sz]e|harden|pen\s*test|malware|"
    r"privilege|escalation|idor|rbac|acl|csp|cors|open\s*redirect|"
    r"path\s+traversal|deserial|rce|remote\s+code|supply\s+chain|"
    r"dependency\s+confusion|leak|pii|gdpr|hipaa"
    r")\b",
    re.IGNORECASE,
)

_BEST_PRACTICES = re.compile(
    r"\b("
    r"best\s+practices?|clean\s+code|solid|dry|kiss|yagni|patterns?|anti-?pattern|"
    r"readability|naming|structure|architecture|separation\s+of\s+concerns|"
    r"error\s+handling|exception|logging|observability|type\s+safety|typing|"
    r"test(?:ing|s)?|coverage|mock|fixture|documentation|docstring|comment|"
    r"performance|latency|memory|complexity|duplication|dead\s+code|"
    r"style|formatting|lint|convention|api\s+design|interface|"
    r"async|concurrency|race\s+condition|resource\s+leak|"
    r"maintainability|scalability|modularity|coupling|cohesion"
    r")\b",
    re.IGNORECASE,
)

_DEV_CONTEXT = re.compile(
    r"\b("
    r"code|diff|patch|function|method|class|module|file|repo|git|"
    r"commit|branch|merge|deploy|endpoint|handler|component|library|"
    r"implementation|snippet|change\s+set|pull\s*request|\bpr\b"
    r")\b",
    re.IGNORECASE,
)

_OUT_OF_SCOPE = re.compile(
    r"(^|\b)("
    r"hello|hi\b|hey\b|thanks|thank\s+you|how\s+are\s+you|"
    r"joke|poem|story|weather|recipe|sports?|movie|"
    r"translate|summarize\s+this\s+article|write\s+me\s+a|"
    r"what\s+is\s+the\s+capital|who\s+won|"
    r"homework|essay|tutor|"
    r"best\s+restaurant|dating\s+advice"
    r")(\b|$)",
    re.IGNORECASE,
)


def is_in_scope(data: dict[str, Any]) -> tuple[bool, str | None]:
    """Return (allowed, denial_message). denial_message set when not allowed."""
    if data.get("diff") or data.get("files"):
        return True, None

    if data.get("mode") in ("ci", "pr"):
        if data.get("pr_number") and data.get("owner") and data.get("repo"):
            return True, None
        if data.get("diff"):
            return True, None

    prompt = str(data.get("prompt", "")).strip()
    if not prompt:
        return False, DENIAL_MESSAGE

    if _OUT_OF_SCOPE.search(prompt):
        return False, DENIAL_MESSAGE

    if (
        _REVIEW_INTENT.search(prompt)
        or _SECURITY_TOPIC.search(prompt)
        or _BEST_PRACTICES.search(prompt)
        or _DEV_CONTEXT.search(prompt)
    ):
        return True, None

    focus = data.get("focus")
    if isinstance(focus, list) and any(
        str(f).lower() in {"security", "best_practices", "quality", "code_quality"}
        for f in focus
    ):
        return True, None

    return False, DENIAL_MESSAGE
