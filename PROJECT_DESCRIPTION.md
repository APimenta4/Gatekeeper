# Project Description — Gatekeeper

## Overview

**Gatekeeper** is a developer-facing security CLI tool built for the MESW SES 2025/2026 course (Group 3). Its goal is to make Static Application Security Testing (SAST) effortless by running multiple industry-standard tools in a single command, providing instant feedback without polluting the developer's local environment.

Gatekeeper integrates with Git via a **pre-commit hook**, automatically scanning code on every commit, and also supports on-demand scanning.

---

## Group Members

| Name |
|------|
| Gonçalo Araújo Guimarães Cardoso Sampaio |
| Gonçalo de Almeida Pinto e Morais de Castro |
| Afonso da Cruz Pimenta |
| José Pedro Pereira da Costa |

---

## Problem Statement

Running multiple SAST tools across a polyglot codebase is complex: each tool has its own installation process, configuration format, and output schema. Developers often skip security scanning entirely because the setup overhead is too high.

Gatekeeper solves this by wrapping all SAST tools inside a single Docker image, exposing a unified CLI, and hooking into Git so scans happen automatically at commit time.

---

## Architecture

```
Developer machine
│
├── gatekeeper (Python CLI — installed via pipx)
│   ├── gatekeeper setup   → installs the pre-commit hook into the target repo
│   └── gatekeeper scan    → invokes the Docker scanning engine
│
└── Docker container (gatekeeper-scanner image)
    ├── Pre-installed SAST tools (installed at image build time via tools-config.yaml)
    ├── Target repository mounted as a volume
    └── docker_scan_command_entrypoint.py → orchestrates tool execution & output
```

The CLI is built with **Click** and the scanning engine runs inside a **Docker** container to ensure a consistent, isolated environment across operating systems and to avoid dependency conflicts on the developer's machine.

Tool configuration is fully declarative and lives in [`tools-config.yaml`](gatekeeper/tools-config.yaml) — adding a new SAST tool requires no code changes.

---

## Key Features

- **Pre-commit integration** — security checks run automatically on every `git commit`
- **On-demand scanning** — run `gatekeeper scan` at any time
- **Docker-isolated execution** — tools run inside a container; nothing is installed on the host
- **Declarative tool config** — add/remove SAST tools by editing `tools-config.yaml`
- **Polyglot support** — language-specific tools are selected based on file extensions detected in the repo
- **Verbose mode** — `gatekeeper scan --verbose` streams live Docker output to the terminal
- **Structured logging** — scan progress and results are logged in a structured format

---

## SAST Tools Integrated

### Generic (run on every codebase)

| Tool | Purpose |
|------|---------|
| [Semgrep](https://semgrep.dev/) | Multi-language static analysis with community rule sets |
| [Trivy](https://trivy.dev/) | Vulnerability scanner for dependencies, IaC, and container images |

### Language-Specific

| Language | Tool | Status |
|----------|------|--------|
| Python | [Bandit](https://bandit.readthedocs.io/) | Implemented |
| Go | [gosec](https://github.com/securego/gosec) | Implemented |
| JavaScript / TypeScript | [ESLint](https://eslint.org/) + `eslint-plugin-security` | Planned |
| Java | [SpotBugs](https://spotbugs.github.io/) + FindSecBugs | Planned |
| C / C++ | [Flawfinder](https://dwheeler.com/flawfinder/) | Planned |
| PHP | [Progpilot](https://github.com/designsecurity/progpilot) | Planned |

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| CLI framework | [Click](https://click.palletsprojects.com/) |
| Package management | [uv](https://docs.astral.sh/uv/) |
| Global install | [pipx](https://pipx.pypa.io/) |
| Pre-commit hooks | [pre-commit](https://pre-commit.com/) |
| Scanning isolation | [Docker](https://www.docker.com/) |
| Code quality | flake8, black, isort, mypy |

---

## Repository Structure

```
project-mesw-sse-2526-g03/
├── README.md
├── PROJECT_DESCRIPTION.md       ← you are here
└── gatekeeper/
    ├── src/gatekeeper/
    │   ├── cli.py               ← CLI entry point
    │   ├── defaults.py          ← default configuration values
    │   ├── commands/
    │   │   ├── scan/            ← scan command logic
    │   │   └── setup/           ← setup command logic
    │   └── utils/
    │       ├── docker.py        ← Docker interaction helpers
    │       ├── git.py           ← Git helpers
    │       ├── printer.py       ← terminal output utilities
    │       └── sast_tools.py    ← tool selection and orchestration
    ├── docker/
    │   ├── Dockerfile           ← scanning engine base image
    │   ├── docker_install_tools_image_step.py
    │   └── docker_scan_command_entrypoint.py
    ├── tools-config.yaml        ← declarative SAST tool configuration
    ├── pyproject.toml
    ├── README.md                ← setup and usage instructions
    ├── DEV_DOCS.md              ← developer documentation
    └── IMPROVEMENTS.md          ← known gaps and planned work
```

---

## Current Limitations

- The pre-commit hook scans the **entire repository** on every commit, not just changed files — this increases scan time on large codebases.
- Directories like `.venv`, `node_modules`, `dist`, and `build` are currently not excluded from scans.
- Tool output is collected as raw JSON files but there is no unified **findings parser** or policy engine to enforce pass/fail thresholds.
- Several language-specific tools listed above are not yet implemented (see `IMPROVEMENTS.md`).
- Pre-commit hooks cannot stream output in real time; results are only visible after the hook finishes.

---

## Quick Start

```bash
# 1. Install Gatekeeper
pipx install .

# 2. Build the scanning Docker image (from the gatekeeper/ directory)
docker build -f docker/Dockerfile -t gatekeeper-scanner .

# 3. Set up the pre-commit hook in any git repository
cd /path/to/your/repo
gatekeeper setup

# 4. Or run a scan on demand
gatekeeper scan
gatekeeper scan --verbose   # stream live output
```

For full details, see [`gatekeeper/README.md`](gatekeeper/README.md).
