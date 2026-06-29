"""
INTENTIONALLY VULNERABLE — SAST/CodeQL demo fixtures (KPI #15).

DO NOT DEPLOY. These endpoints take untrusted HTTP input (a recognized
*remote* taint source for CodeQL) and feed it straight into dangerous sinks so
the CodeQL default query suite raises real code-scanning alerts:

  * py/command-line-injection
  * py/code-injection
  * py/sql-injection
  * py/path-injection
"""
import os
import sqlite3
import subprocess

from flask import Flask, request

app = Flask(__name__)


@app.route("/ping")
def ping():
    # py/command-line-injection: remote input -> shell
    host = request.args.get("host", "")
    return os.popen("ping -c 1 " + host).read()


@app.route("/run")
def run():
    # py/command-line-injection: remote input -> subprocess with shell=True
    cmd = request.args.get("cmd", "")
    return subprocess.check_output(cmd, shell=True)


@app.route("/calc")
def calc():
    # py/code-injection: remote input -> eval
    expr = request.args.get("expr", "0")
    return str(eval(expr))


@app.route("/user")
def user():
    # py/sql-injection: remote input concatenated into a query
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = '" + name + "'")
    return str(cur.fetchall())


@app.route("/read")
def read():
    # py/path-injection: remote input -> filesystem path
    name = request.args.get("file", "")
    with open("/var/data/" + name) as fh:
        return fh.read()


if __name__ == "__main__":
    app.run()
