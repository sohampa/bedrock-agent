# AWS CI/CD (single account, us-east-1)

Foundry-style pipeline implemented with **GitHub Actions** + **AgentCore**.

| Stage | Workflow | What it does |
| --- | --- | --- |
| 1. Code | *(repo)* | `app/MyAgent/`, `agentcore/agentcore.json` |
| 2. CI | `ci-agent.yml` | ruff, bandit, pytest, scope gate, `agentcore validate` |
| 2b. CI deploy | `ci-agent.yml` → `deploy-dev` | Auto `agentcore deploy --target dev` on push to `main` |
| 3. CD promote | `cd-deploy.yml` | Manual deploy to `staging` or `prod` |
| PR review | `agent-code-review.yml` | Security review via deployed **dev** agent |
| 4. Runtime | AgentCore | Bedrock Nova in **us-east-1** |
| 5. Monitor | CLI | `agentcore logs`, `agentcore traces`, `agentcore status` |

All targets use the **same account** and **`us-east-1`** — see `agentcore/aws-targets.json`.

---

## Step 1 — AWS targets (done in repo)

`agentcore/aws-targets.json` defines:

- `dev`, `staging`, `prod` → same `account`, `region: us-east-1`

Update the account ID if you use a different AWS account.

---

## Step 2 — GitHub secrets

Repository → **Settings** → **Secrets and variables** → **Actions**:

| Secret | Purpose |
| --- | --- |
| `AWS_ACCESS_KEY_ID` | Deploy + invoke Bedrock/AgentCore |
| `AWS_SECRET_ACCESS_KEY` | Pair with above |
| `GITHUB_TOKEN` | Default token usually works for PR comments |

IAM user/role needs at minimum:

- Bedrock invoke (Nova Pro in us-east-1)
- AgentCore deploy permissions (CDK/CloudFormation from `agentcore deploy`)

---

## Step 3 — GitHub environments (optional approvals)

**Settings** → **Environments** → create:

| Environment | Used for |
| --- | --- |
| `dev` | Auto deploy from `main` |
| `staging` | Manual `cd-deploy.yml` → staging |
| `production` | Manual `cd-deploy.yml` → prod |

Add **required reviewers** on `staging` and `production` for HITL gates.

---

## Step 4 — First deploy (local, once)

**Windows** — set `UV_LINK_MODE=copy` before deploy (fixes CDK synth / uv hardlink error):

```powershell
cd d:\Soham-workspace\AWS\AgentCore\MyAgent
$env:UV_LINK_MODE = "copy"
$env:AWS_REGION = "us-east-1"
aws configure   # account with us-east-1 access
agentcore validate
agentcore deploy --target dev
# or: .\scripts\deploy-dev.ps1
agentcore status --target dev
```

Enable **Amazon Nova Pro** in Bedrock (us-east-1).

---

## Step 5 — Enable CI/CD

1. Push to GitHub (`main` branch).
2. Open **Actions** → **CI — Agent validate** runs on every PR and push.
3. On push to `main`, **deploy-dev** runs after CI passes.
4. Promote manually: **Actions** → **CD — Promote staging / prod** → Run workflow → choose `staging` or `prod`.
5. PRs trigger **PR — Agent security review** (needs dev deployed).

---

## Step 6 — Monitor (stage 5)

```powershell
agentcore status --target dev
agentcore logs --runtime MyAgent
agentcore traces list --runtime MyAgent
```

Optional later:

```bash
agentcore add evaluator
agentcore add online-eval
agentcore deploy --target dev
```

---

## Workflow diagram

```
PR / push
    │
    ▼
ci-agent.yml ──► lint, bandit, pytest, scope, validate
    │
    ├── push main ──► deploy-dev (us-east-1, target dev)
    │
PR ──► agent-code-review.yml ──► invoke dev agent + PR comment

Manual: cd-deploy.yml ──► staging | prod (us-east-1)
```

---

## Troubleshooting

| Issue | Fix |
| --- | --- |
| Deploy fails | Run `agentcore validate`; check IAM and `aws-targets.json` account |
| CDK synth failed / uv hardlink (Windows) | `$env:UV_LINK_MODE = "copy"` then redeploy, or `.\scripts\deploy-dev.ps1` |
| CDK bootstrap / SSM AccessDenied | Run `cdk bootstrap aws://ACCOUNT/us-east-1` and grant `ssm:GetParameter` on `/cdk-bootstrap/*` (see below) |

### First-time CDK bootstrap (same account, us-east-1)

AgentCore deploy uses AWS CDK. Bootstrap once per account+region:

```powershell
cd agentcore\cdk
npm install
npx cdk bootstrap aws://543816070942/us-east-1
```

Your IAM user/role also needs CDK deploy permissions, including:

- `ssm:GetParameter` on `arn:aws:ssm:us-east-1:543816070942:parameter/cdk-bootstrap/*`
- CloudFormation create/update
- IAM pass-role for CDK bootstrap roles (often via `AdministratorAccess` or the CDK deploy policy)
| Invoke fails | Deploy dev first; Bedrock Nova enabled; billing valid |
| PR review 403 | Deploy not complete; wrong `--target` |
| CI path errors | Workflows assume repo root is `MyAgent` folder |
