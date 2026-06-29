/*
 * INTENTIONALLY VULNERABLE — SAST/CodeQL demo fixtures (KPI #15).
 *
 * DO NOT DEPLOY. These routes take untrusted HTTP input (a recognized *remote*
 * taint source for CodeQL) and feed it into dangerous sinks so the CodeQL
 * default query suite raises real code-scanning alerts:
 *
 *   - js/command-line-injection
 *   - js/code-injection
 *   - js/path-injection
 */
const express = require("express");
const cp = require("child_process");
const fs = require("fs");

const app = express();

app.get("/ping", (req, res) => {
  // js/command-line-injection: remote input -> shell
  const host = req.query.host;
  cp.exec("ping -c 1 " + host, (err, stdout) => res.send(stdout));
});

app.get("/calc", (req, res) => {
  // js/code-injection: remote input -> eval
  const expr = req.query.expr;
  res.send(String(eval(expr)));
});

app.get("/read", (req, res) => {
  // js/path-injection: remote input -> filesystem path
  const name = req.query.file;
  fs.readFile("/var/data/" + name, "utf8", (err, data) => res.send(data));
});

app.listen(3000);
