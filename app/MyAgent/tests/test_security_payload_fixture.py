import json
from pathlib import Path


def test_poc_security_payload_fixture_is_valid_ci_payload():
    repo_root = Path(__file__).resolve().parents[3]
    fixture_path = repo_root / "scripts" / "test-security-payload-poc.json"

    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert payload["mode"] == "ci"
    assert "diff --git" in payload["diff"]
    assert "subprocess.run" in payload["diff"]
    assert "shell=True" in payload["diff"]
    assert "eval(" in payload["diff"]
