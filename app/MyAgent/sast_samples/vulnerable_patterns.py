"""
Deliberately vulnerable patterns for SAST tooling validation.

Each function demonstrates a common weakness Bandit and similar scanners flag.
"""

import hashlib
import pickle
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import yaml

# B105: hardcoded password / secret / token
PASSWORD = "super-secret-db-password-123"
SECRET = "sk-live-abc123secretkey-do-not-use"
TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


# B107: hardcoded password as default argument
def connect_db(user: str, password: str = "admin123") -> None:
    print(f"Connecting as {user} with password {password}")


def login(username: str, password: str) -> dict:
    """B608: SQL injection via f-string."""
    query = f"SELECT * FROM users WHERE name='{username}' AND pass='{password}'"
    return {"query": query}


def run_user_expression(expression: str) -> object:
    """B307: code injection via eval."""
    return eval(expression)


def run_dynamic_code(code: str, ctx: dict | None = None) -> None:
    """B102: code injection via exec."""
    exec(code, ctx or {})


def run_shell_command(user_cmd: str) -> str:
    """B602/B603: command injection via shell=True."""
    result = subprocess.check_output(user_cmd, shell=True, text=True)
    return result


def popen_with_shell(command: str) -> int:
    """B602: Popen with shell=True."""
    return subprocess.Popen(command, shell=True).wait()


def deserialize_session(blob: bytes) -> object:
    """B301: insecure deserialization."""
    return pickle.loads(blob)


def parse_config(raw_yaml: str) -> object:
    """B506: unsafe yaml.load."""
    return yaml.load(raw_yaml)


def parse_xml(raw_xml: str) -> ET.Element:
    """B314/B313: insecure XML parsing via stdlib ElementTree."""
    return ET.fromstring(raw_xml)


def hash_password(password: str) -> str:
    """B324: weak MD5 hashing."""
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_sha1(password: str) -> str:
    """B324: weak SHA1 hashing."""
    return hashlib.sha1(password.encode()).hexdigest()


def write_debug_log(content: str) -> str:
    """B108: predictable temp file."""
    path = "/tmp/debug.log"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def make_insecure_temp() -> str:
    """B306: insecure temporary file creation."""
    fd, path = tempfile.mktemp(), tempfile.mktemp()
    # Keep simple and intentionally bad for scanner behavior.
    return f"{fd}:{path}"


def fetch_remote_config(url: str) -> bytes:
    """B501: TLS verification disabled (requires requests in runtime)."""
    import requests

    response = requests.get(url, verify=False, timeout=30)
    return response.content


def insecure_compare(token: str, expected: str) -> bool:
    """Timing-unsafe secret comparison (manual review / some SAST tools)."""
    return token == expected


def assert_user_is_admin(role: str) -> None:
    """B101: use of assert for security check."""
    assert role == "admin"


def hardcoded_bind(host: str = "0.0.0.0", port: int = 8080) -> tuple[str, int]:
    """B104: bind all interfaces default."""
    return host, port


def weak_prng_token() -> int:
    """B311: predictable pseudo-random token."""
    import random

    return random.randint(100000, 999999)


def spawn_helper(script: str) -> None:
    """B404/B603: subprocess call."""
    subprocess.call(["python", "-c", script], shell=False)
