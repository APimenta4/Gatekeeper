# Gatekeeper

Gatekeeper is a developer-facing security CLI that runs multiple SAST tools in a single command and gives instant feedback — before code ever leaves your machine.

It hooks into Git via a pre-commit hook so scans happen automatically on every `git commit`, and also supports on-demand scanning. All tools run inside a Docker container so nothing is installed on the host.


## Requirements

- Python 3.13+
- Git
- Docker (must be running)
- `pipx` — `pip install pipx`

## Installation

From the `gatekeeper/` directory:

```bash
# 1. Install the CLI globally
pipx install .

# 2. Build the Docker scanning image
docker build -f docker/Dockerfile -t gatekeeper-scanner .
```

> **Note:** Step 2 takes a few minutes on first run (downloads and installs all SAST tools into the image). You only need to repeat it if you change `docker/Dockerfile`, `docker/docker_scan_command_entrypoint.py`, `docker/docker_install_tools_image_step.py`, or `tools-config.yaml`.


## Usage

### Wire up the pre-commit hook

Run this once inside any Git repository you want to protect:

```bash
cd /path/to/your/repo
gatekeeper setup
```

By default, the hook runs `gatekeeper scan` with finding messages enabled.
If you prefer a cleaner pre-commit output, install the hook like this:

```bash
gatekeeper setup --no-details
```

From that point on, `gatekeeper scan` runs automatically on every `git commit`. The commit is blocked if any finding is classified as **BLOCK** by the policy engine.

### Run a scan on demand

```bash
gatekeeper scan                # standard output
gatekeeper scan --verbose      # stream live Docker output to the terminal
gatekeeper scan --no-report    # skip generating the HTML dashboard
gatekeeper scan --no-details   # cleaner terminal output (no per-finding messages)
```

Exit code `0` = no blockers. Exit code `1` = at least one finding was BLOCKED.

## SAST tools

Gatekeeper runs **Semgrep** and **Trivy** on every codebase, plus a language-specific tool selected by file extension:

| Language | Tool |
|----------|------|
| Python | Bandit |
| JavaScript / TypeScript | ESLint + `eslint-plugin-security` |
| Java | SpotBugs + FindSecBugs |
| Go | gosec |
| C / C++ | Flawfinder |
| PHP | Progpilot |


## Policy Engine

The heart of Gatekeeper is a pure-Python rule engine (`src/gatekeeper/policy/`). Each rule is a `Rule` object with a predicate and a verdict — no YAML, no config files.

Findings are classified into three states:

| Verdict | Meaning |
|---------|---------|
| `BLOCK` | Commit is vetoed. Developer must fix before proceeding. |
| `WARN` | Finding is reported but does not block the commit. |
| `ALLOW` | Finding is below the policy threshold. Silently passes. |

**Default rules** (all match on the `cwe` field populated by parsers):

| Rule ID | Name | Predicate | Verdict | Rationale |
|---------|------|-----------|---------|-----------|
| GK-001 | Command Injection | `cwe == "CWE-78"` | BLOCK | Arbitrary shell execution; no severity threshold — even LOW is dangerous |
| GK-002 | SQL Injection (severe) | `cwe == "CWE-89"` + HIGH/CRITICAL | BLOCK | Directly exploitable query construction |
| GK-003 | SQL Injection (moderate) | `cwe == "CWE-89"` + MEDIUM | WARN | Exploitable under specific conditions; needs review |
| GK-004 | Path Traversal | `cwe == "CWE-22"` | BLOCK | Attack surface is the entire filesystem |
| GK-005 | Hardcoded Credentials | `cwe in {CWE-798, CWE-259}` | BLOCK | Permanently compromised once the repo is cloned |
| GK-006 | Insecure Deserialization | `cwe == "CWE-502"` | BLOCK | `pickle.load` / `yaml.load` → arbitrary code execution |
| GK-007 | Cross-Site Scripting | `cwe == "CWE-79"` | WARN | Context-dependent; framework escaping may mitigate |
| GK-008 | Weak Cryptography | `cwe == "CWE-327"` | WARN | MD5/SHA-1/DES vulnerable to brute-force; migrate to modern algorithms |

All rules run against every finding. If multiple rules match, the highest-precedence verdict wins (`BLOCK > WARN > ALLOW`). Findings with no matching rule are **ALLOWed**.

To add a custom rule, append a `Rule(...)` to `default_rules` in `src/gatekeeper/policy/rules.py`.





