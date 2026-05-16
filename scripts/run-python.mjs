#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const args = process.argv.slice(2);

if (args.length === 0) {
  console.error("usage: node scripts/run-python.mjs <python-args...>");
  process.exit(2);
}

const uvPackages = [
  "--with",
  "fastapi",
  "--with",
  "httpx",
  "--with",
  "jsonschema",
  "--with",
  "openai",
  "--with",
  "pydantic",
  "--with",
  "psycopg[binary]",
  "--with",
  "pyyaml",
  "--with",
  "sqlalchemy",
  "--with",
  "uvicorn[standard]",
];

const venvPython =
  process.platform === "win32"
    ? path.join(root, ".venv", "Scripts", "python.exe")
    : path.join(root, ".venv", "bin", "python");

const candidates = [];

if (process.env.PYTHON) {
  candidates.push({ command: process.env.PYTHON, prefix: [] });
}

if (existsSync(venvPython)) {
  candidates.push({ command: venvPython, prefix: [] });
}

candidates.push({ command: "python", prefix: [] });
candidates.push({ command: "python3", prefix: [] });
candidates.push({
  command: "uv",
  prefix: ["run", "--python", "3.11", ...uvPackages, "python"],
});

for (const candidate of candidates) {
  const probe = spawnSync(
    candidate.command,
    [...candidate.prefix, "-c", "import sys; print(sys.executable)"],
    {
      cwd: root,
      stdio: "ignore",
      shell: false,
    }
  );

  if (probe.status !== 0) {
    continue;
  }

  const completed = spawnSync(candidate.command, [...candidate.prefix, ...args], {
    cwd: root,
    stdio: "inherit",
    shell: false,
  });

  if (completed.error) {
    continue;
  }

  process.exit(completed.status ?? 1);
}

console.error("Python executable not found. Install Python 3.11 or uv.");
process.exit(127);
