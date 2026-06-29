# SAST vulnerability samples (intentional — do not merge to main)

This directory contains **deliberately insecure code** for testing Static Application Security Testing (SAST) tools such as **Bandit** (used in CI) and SonarQube.

**Do not import these modules from production code.** They exist only on the `test/sast-vulnerability-samples` branch.

## Run Bandit locally

```powershell
cd app/MyAgent
uv run bandit -r sast_samples/ -ll
```

Expect **multiple findings** (non-zero exit code).

## Scan the full app (CI-equivalent)

```powershell
cd app/MyAgent
uv run bandit -r . -x ./.venv -ll
```

CI will **fail** on this branch because Bandit scans the entire `app/MyAgent` tree.

## Expected findings

| File | Pattern | Typical Bandit ID | CWE |
| --- | --- | --- | --- |
| `vulnerable_patterns.py` | Hardcoded API key / password | B105, B106 | CWE-798 |
| `vulnerable_patterns.py` | SQL string concatenation | B608 | CWE-89 |
| `vulnerable_patterns.py` | `eval()` on user input | B307 | CWE-95 |
| `vulnerable_patterns.py` | `subprocess` with `shell=True` | B602, B603 | CWE-78 |
| `vulnerable_patterns.py` | `pickle.loads` | B301 | CWE-502 |
| `vulnerable_patterns.py` | `yaml.load` without SafeLoader | B506 | CWE-20 |
| `vulnerable_patterns.py` | MD5 for password hashing | B324 | CWE-327 |
| `vulnerable_patterns.py` | Insecure temp file | B108 | CWE-377 |
| `insecure_api.py` | Path traversal | B202 (custom) / manual | CWE-22 |
| `insecure_api.py` | Debug mode enabled | B201 | CWE-489 |

## Testing the code review agent

Use the diff from this branch in a review payload to verify the agent flags the same issues:

```powershell
git diff main...HEAD -- app/MyAgent/sast_samples/ > sast_samples.diff
```

Paste the diff into `scripts/test-security-payload.json` or invoke the agent with a PR containing this branch.
