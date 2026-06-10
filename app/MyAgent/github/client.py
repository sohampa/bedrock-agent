import json
import os
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

_ALLOWED_GITHUB_HOSTS = frozenset({"api.github.com", "github.com"})


class GitHubError(Exception):
    pass


def _token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise GitHubError(
            "GITHUB_TOKEN (or GH_TOKEN) is not set. "
            "Create a fine-grained or classic PAT with repo scope for PR read/write."
        )
    return token


def _validate_github_https_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise GitHubError(f"Refusing non-HTTPS GitHub URL: {url}")
    if parsed.hostname not in _ALLOWED_GITHUB_HOSTS:
        raise GitHubError(f"Refusing unexpected GitHub URL host: {parsed.hostname}")
    return url


def _github_urlopen(req: urllib.request.Request, timeout: int):
    """Open a validated GitHub HTTPS URL only."""
    _validate_github_https_url(req.full_url)
    return urllib.request.urlopen(req, timeout=timeout)  # nosec B310


def _request(method: str, url: str, body: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {_token()}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "agentcore-code-review-agent",
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        _validate_github_https_url(url), data=data, headers=headers, method=method
    )
    try:
        with _github_urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise GitHubError(f"GitHub API {e.code} for {url}: {detail}") from e


def fetch_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Return unified diff for a pull request."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    pr = _request("GET", url)
    diff_url = pr.get("diff_url")
    if not diff_url:
        raise GitHubError("Pull request response did not include diff_url")

    headers = {
        "Accept": "application/vnd.github.diff",
        "Authorization": f"Bearer {_token()}",
        "User-Agent": "agentcore-code-review-agent",
    }
    req = urllib.request.Request(
        _validate_github_https_url(diff_url), headers=headers, method="GET"
    )
    try:
        with _github_urlopen(req, timeout=120) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise GitHubError(f"Failed to download diff: {e.code} {detail}") from e


def post_pr_comment(owner: str, repo: str, pr_number: int, body: str) -> str:
    """Post a top-level comment on the pull request. Returns comment HTML URL."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    result = _request("POST", url, {"body": body})
    return result.get("html_url", "comment posted")
