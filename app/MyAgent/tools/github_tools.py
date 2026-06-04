from strands import tool

from github.client import GitHubError, fetch_pr_diff, post_pr_comment


@tool
def fetch_github_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Fetch the unified diff for a GitHub pull request.

    Args:
        owner: GitHub org or user (e.g. "my-org").
        repo: Repository name (e.g. "my-service").
        pr_number: Pull request number (e.g. 42).
    """
    try:
        return fetch_pr_diff(owner, repo, pr_number)
    except GitHubError as e:
        return f"Error fetching PR diff: {e}"


@tool
def post_github_pr_review_comment(
    owner: str, repo: str, pr_number: int, body: str
) -> str:
    """Post a code review summary as a comment on a GitHub pull request.

    Args:
        owner: GitHub org or user.
        repo: Repository name.
        pr_number: Pull request number.
        body: Full markdown review text to post.
    """
    try:
        url = post_pr_comment(owner, repo, pr_number, body)
        return f"Posted review comment: {url}"
    except GitHubError as e:
        return f"Error posting PR comment: {e}"
