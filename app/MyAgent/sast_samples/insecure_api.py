"""
Flask-style API handlers with intentional security flaws (no Flask dependency).
Used only to exercise SAST rules on web-app patterns.
"""

import base64
import hashlib
import os

# B201: flask debug mode (pattern match even without running Flask)
DEBUG = True
app_config = {"DEBUG": True, "TESTING": True}


def read_user_file(base_dir: str, filename: str) -> str:
    """Path traversal: user controls filename without sanitization."""
    full_path = os.path.join(base_dir, filename)
    with open(full_path, encoding="utf-8") as f:
        return f.read()


def render_greeting(name: str) -> str:
    """Reflected XSS pattern (HTML injection)."""
    return f"<h1>Hello, {name}!</h1>"


def redirect_url(next_url: str) -> str:
    """Open redirect — no allowlist validation."""
    return f"Location: {next_url}"


def execute_raw_sql(cursor, table: str, column: str, value: str) -> None:
    """Dynamic SQL with string formatting."""
    sql = "SELECT * FROM %s WHERE %s = '%s'" % (table, column, value)
    cursor.execute(sql)


def load_env_secret() -> str:
    """Fallback hardcoded secret when env var missing."""
    secret = os.environ.get("APP_SECRET")
    if not secret:
        secret = "fallback-jwt-secret-not-from-vault"
    return secret


def build_set_cookie_header(session_id: str) -> str:
    """Session cookie without Secure/HttpOnly/SameSite flags."""
    return f"Set-Cookie: sid={session_id}; Path=/"


def insecure_token_payload(user_id: str, role: str) -> str:
    """JWT-like token built without signature validation guarantees."""
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(
        f'{{"sub":"{user_id}","role":"{role}"}}'.encode()
    ).decode().rstrip("=")
    return f"{header}.{payload}."


def check_password_fast(candidate: str, expected_hash: str) -> bool:
    """Weak and timing-unsafe password check."""
    candidate_hash = hashlib.md5(candidate.encode()).hexdigest()
    return candidate_hash == expected_hash


def cors_allow_all(origin: str) -> dict:
    """Overly permissive CORS policy."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Vary": origin,
    }
