import re
from typing import Any

DENIAL_MESSAGE = """I'm a **security code review** agent only. I can review diffs and pull requests for security issues (vulnerabilities, auth, secrets, injection, unsafe APIs, etc.).

I can't help with general chat, non-security coding questions, or tasks outside security review.

**To get a review, send:**
- `mode`: `ci` or `pr` with a `diff`, or GitHub `owner` / `repo` / `pr_number`
- A `prompt` focused on security (e.g. "Review this change for security issues")
"""

# Structured review requests (CI / PR) are always in scope.
_STRUCTURED_REVIEW = re.compile(
    r"\b(review|audit|scan|analyze|analyse)\b.*\b("
    r"security|vulnerabilit|owasp|threat|harden|cve|secret|auth|injection|xss|csrf|"
    r"diff|pull\s*request|pr\b|patch|change\s*set|code\s*change"
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

_OUT_OF_SCOPE = re.compile(
    r"(^|\b)("
    r"hello|hi\b|hey\b|thanks|thank\s+you|how\s+are\s+you|"
    r"joke|poem|story|weather|recipe|sports?|movie|"
    r"translate|summarize\s+this\s+article|write\s+me\s+a|"
    r"what\s+is\s+the\s+capital|who\s+won|"
    r"homework|essay|tutor|"
    r"performance\s+only|style\s+only|formatting\s+only|readability\s+only|"
    r"unit\s+test\s+help|debug\s+my|fix\s+my\s+bug|explain\s+python\s+basics|"
    r"best\s+restaurant|dating\s+advice"
    r")(\b|$)",
    re.IGNORECASE,
)

_NON_SECURITY_REVIEW = re.compile(
    r"\b(review|check|audit)\b.*\b("
    r"style|formatting|readability|naming|performance|speed|latency|"
    r"documentation\s+only|typo|grammar|ui\s+ux|design\s+only|"
    r"test\s+coverage\s+only|refactor\s+style"
    r")\b",
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

    if _NON_SECURITY_REVIEW.search(prompt):
        return False, DENIAL_MESSAGE

    if _STRUCTURED_REVIEW.search(prompt) or _SECURITY_TOPIC.search(prompt):
        return True, None

    focus = data.get("focus")
    if isinstance(focus, list) and any(
        str(f).lower() == "security" for f in focus
    ):
        return True, None

    # Short generic prompts without security context
    if len(prompt.split()) <= 4 and not _SECURITY_TOPIC.search(prompt):
        return False, DENIAL_MESSAGE

    return False, DENIAL_MESSAGE
