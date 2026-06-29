"""
Deliberately vulnerable patterns for SAST tooling validation.

Each function demonstrates a common weakness Bandit and similar scanners flag.
"""

import hashlib
import pickle
import subprocess

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


def run_shell_command(user_cmd: str) -> str:
    """B602/B603: command injection via shell=True."""
    result = subprocess.check_output(user_cmd, shell=True, text=True)
    return result


def deserialize_session(blob: bytes) -> object:
    """B301: insecure deserialization."""
    return pickle.loads(blob)


def parse_config(raw_yaml: str) -> object:
    """B506: unsafe yaml.load."""
    return yaml.load(raw_yaml)


def hash_password(password: str) -> str:
    """B324: weak MD5 hashing."""
    return hashlib.md5(password.encode()).hexdigest()


def write_debug_log(content: str) -> str:
    """B108: predictable temp file."""
    path = "/tmp/debug.log"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def fetch_remote_config(url: str) -> bytes:
    """B501: TLS verification disabled (requires requests in runtime)."""
    import requests

    response = requests.get(url, verify=False, timeout=30)
    return response.content


def insecure_compare(token: str, expected: str) -> bool:
    """Timing-unsafe secret comparison (manual review / some SAST tools)."""
    return token == expected


def spawn_helper(script: str) -> None:
    """B404/B603: subprocess call."""
    subprocess.call(["python", "-c", script], shell=False)
