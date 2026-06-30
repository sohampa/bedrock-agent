"""Intentional insecure patterns for SAST/CodeQL/Bandit testing only."""

import hashlib
import subprocess


def insecure_eval(user_expression: str):
    return eval(user_expression)  # noqa: S307


def insecure_shell(command: str):
    return subprocess.run(command, shell=True, capture_output=True, text=True, check=False)


def weak_password_hash(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()
