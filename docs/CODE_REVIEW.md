# Code review agent (CI + GitHub PR)

This agent reviews diffs and pull requests for **security issues** and **developer best practices** (error handling, testing, maintainability, naming, structure, performance tied to the change). General chat and off-topic requests are **denied** before the model runs.

## Prerequisites

1. **AWS:** Credentials with Bedrock access; Nova Pro enabled in your region.
2. **Deploy:** `agentcore deploy` from the `MyAgent` directory (after `aws-targets.json` is configured).
3. **GitHub:** `GITHUB_TOKEN` with `pull-requests: read` (and `write` if posting comments).

Local dev: add secrets to `agentcore/.env.local`:

```env
GITHUB_TOKEN=ghp_...
```

## Invoke payload

| Field | Description |
| --- | --- |
| `prompt` | Review instructions |
| `mode` | `ci`, `pr`, or `chat` |
| `diff` | Unified diff text (CI) |
| `owner`, `repo`, `pr_number` | GitHub PR context |
| `post_comment` | `true` to post review on the PR |
| `focus` | Optional list; e.g. `["security"]`, `["best_practices"]`, `["quality"]` |

## Out of scope (denied)

- "Hello", general Q&A, jokes, non-coding topics
- Homework, essays, or tutoring unrelated to reviewing code

## In scope (allowed)

- PR/CI payloads with a `diff` or GitHub PR fields
- Security review (vulnerabilities, auth, secrets, injection, etc.)
- Best-practices review (naming, structure, error handling, tests, maintainability)
- Example: `"Review this PR for security and best practices"`

### Local PR review (post comment)

```powershell
cd MyAgent
$env:GITHUB_TOKEN = "ghp_..."
agentcore invoke --dev --prompt-file payload.json
```

`payload.json`:

```json
{
  "prompt": "Review this PR for security and correctness.",
  "mode": "pr",
  "owner": "your-org",
  "repo": "your-repo",
  "pr_number": 42,
  "post_comment": true
}
```

### Local CI-style review (diff only, no GitHub post)

```json
{
  "prompt": "Review this change set.",
  "mode": "ci",
  "diff": "diff --git a/foo.py b/foo.py\n..."
}
```

```powershell
agentcore invoke --dev --prompt-file payload.json
```

## GitHub Actions

Workflow: [`.github/workflows/agentcore.yml`](../.github/workflows/agentcore.yml)

**Secrets:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (or switch to OIDC).

**Variables (optional):** `AGENTCORE_RUNTIME_NAME`, `AGENTCORE_TARGET`, `AGENTCORE_REGION`, `FAIL_ON_CRITICAL`.

The workflow:

1. Fetches the PR diff with `gh pr diff`
2. Invokes the deployed agent via `agentcore invoke`
3. Fails the job if `REVIEW_META` reports `critical` > 0

## Tools

| Tool | Purpose |
| --- | --- |
| `fetch_github_pr_diff` | Load PR patch when diff not in payload |
| `post_github_pr_review_comment` | Publish review markdown on the PR |
