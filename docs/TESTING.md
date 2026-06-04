# Testing the security review agent

## 1. Restart dev (required after code changes)

In the terminal running `agentcore dev`, press **Ctrl+C**, then:

```powershell
cd d:\Soham-workspace\AWS\AgentCore\MyAgent
agentcore dev
```

Open **Chat UI:** http://localhost:8081

## 2. Scope tests (no AWS / Bedrock)

```powershell
cd d:\Soham-workspace\AWS\AgentCore\MyAgent
python scripts\test_scope.py
```

Expect **4/4** passed.

## 3. Web UI — deny off-topic

In the chat box, send:

```text
Hello, how are you?
```

**Expected:** Refusal message (security code review agent only). No Bedrock call.

## 4. Web UI — security review (needs Bedrock)

Paste the full contents of `scripts/test-security-payload.json` as one message.

**Expected:** Security findings (SQL injection, hardcoded secret, etc.) and a `REVIEW_META` footer.

**If you see `INVALID_PAYMENT_INSTRUMENT` or model access errors:**

- Bedrock console → enable **Amazon Nova Pro**
- Billing → valid payment method on the AWS account
- Confirm `app/MyAgent/model/load.py` uses `amazon.nova-pro-v1:0`
- Restart `agentcore dev` after fixes

## 5. CLI invoke (deployed agent only)

`agentcore invoke` calls the **deployed** runtime (no `--dev` flag in CLI v0.16).

```powershell
agentcore invoke --prompt-file scripts\test-denied-payload.json
```

For local HTTP (if agent listens on 8080):

```powershell
curl.exe -X POST http://127.0.0.1:8080/invocations `
  -H "Content-Type: application/json" `
  -d "@scripts/test-denied-payload.json"
```

## Test payloads

| File | Purpose |
| --- | --- |
| `scripts/test-denied-payload.json` | Should be **denied** |
| `scripts/test-security-payload.json` | Should run **security review** |
