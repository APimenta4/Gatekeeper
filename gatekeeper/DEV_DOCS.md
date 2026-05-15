# Developer Documentation

## Technologies used

- **uv** — dependency management, locking, and virtual environment creation
- **click** — CLI framework
- **pipx** — installs the CLI globally in an isolated environment (think `brew` but for Python packages)
- **pre-commit** — manages the Git pre-commit hook that triggers `gatekeeper scan` on every commit
- **Docker** — runs all SAST tools inside a consistent, isolated container; nothing is installed on the host
- **pytest** — unit testing framework (`tests/`)

---

## Architecture

Gatekeeper is structured around two tiers and a pipeline:

```
Host (Python CLI)                    Docker container
────────────────────                 ─────────────────────────────────
gatekeeper scan                      gatekeeper-scanner image
      │                                    │
      ▼                                    ▼
ScanPipeline                         docker_scan_command_entrypoint.py
  ├── ToolSelectionFilter                  ├── Runs tools in parallel threads
  ├── DockerScanFilter  ──── docker run ──▶├── Writes per-tool JSON to /repo/.gatekeeper/
  ├── FindingsParsingFilter ◀─ findings ───┘
  ├── PolicyEvaluationFilter
  └── ReportGenerationFilter
```

### Pipes-and-Filters pipeline

`pipeline/base.py` defines `ScanFilter` (abstract, one method: `process(ctx) -> ctx`) and `ScanPipeline` (iterates filters in order). Filters are composed in `commands/scan/command.py`.

A single `ScanContext` dataclass (`pipeline/context.py`) is passed through every filter and accumulates state:

| Field | Set by | Contains |
|-------|--------|---------|
| `sast_tools` | `ToolSelectionFilter` | Which tools to run, based on file extensions |
| `findings_file_path` | `DockerScanFilter` | Path to the aggregated JSON from the container |
| `raw_findings` | `FindingsParsingFilter` | Raw per-tool JSON |
| `findings` | `FindingsParsingFilter` | Normalised `Finding` objects |
| `decisions` | `PolicyEvaluationFilter` | `Decision` per finding (verdict + matched rules) |
| `violations` | `PolicyEvaluationFilter` | Subset of findings whose verdict is BLOCK |

### Docker scanning

`DockerScanFilter` runs:
```
docker run --rm -v <git_root>:/repo gatekeeper-scanner --tools <names> --output /repo/.gatekeeper/findings.json
```
Inside the container, `docker_scan_command_entrypoint.py` runs each tool in a separate thread, writes individual JSON files, then aggregates them into `findings.json`. The host reads this file back after the container exits.

---

## Adding a new SAST tool

Two steps are required:

### 1. Register the tool in `tools-config.yaml`

Add an entry under `generic_tools` (runs on every repo) or `specific_tools` (runs only when matching file extensions are found):

```yaml
specific_tools:
  - name: MyTool
    supported_file_extensions: [.rb]
    installation_command: gem install my-tool
    execution_command: my-tool --format json --output {output_file} .
```

`{output_file}` is replaced at runtime with the path inside the container.

### 2. Register a parser in `parsers/tools/`

Create `parsers/tools/mytool.py` and decorate it with `@ParserFactory.register("MyTool")` — the name must match `tools-config.yaml` exactly:

```python
from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_MEDIUM

@ParserFactory.register("MyTool")
class MyToolParser(ToolParser):
    def parse(self, data: dict) -> list[Finding]:
        findings = []
        for item in data.get("issues", []):
            findings.append(Finding(
                tool="MyTool",
                file=item["file"],
                line=int(item["line"]),
                severity=item.get("severity", SEVERITY_MEDIUM).upper(),
                message=item["message"],
                cwe=item.get("cwe"),  # e.g. "CWE-78" — populate if the tool provides it
            ))
        return findings
```

Import the new parser in `parsers/tools/__init__.py` so the `@register` decorator fires at import time.

> **Tip:** The `cwe` field on `Finding` is what the policy engine matches on. If your tool exposes CWE IDs in its output, extract them — this is what makes rules like `GK-001` (CWE-78 → BLOCK) fire for findings from your tool.

---

## Policy engine

The policy engine lives in `src/gatekeeper/policy/`. It is pure Python — no YAML, no config files.

### How it works

1. `PolicyEngine(rules)` takes a list of `Rule` objects.
2. `engine.evaluate_all(findings)` runs every rule against every finding.
3. All rules that match a finding are collected; the highest-precedence verdict wins (`BLOCK > WARN > ALLOW`).
4. Returns a `list[Decision]`, where each `Decision` carries the original `Finding`, the final `Verdict`, and the list of rules that matched.

### Adding a new rule

Open `src/gatekeeper/policy/rules.py` and append a `Rule` to `default_rules`:

```python
Rule(
    id="GK-009",
    name="XML External Entity",
    description=(
        "CWE-611: XXE allows attackers to read arbitrary files or perform SSRF "
        "via malicious XML input. Blocked unconditionally."
    ),
    predicate=lambda f: f.cwe == "CWE-611",
    verdict=Verdict.BLOCK,
),
```

Fields:
- `id` — unique identifier, shown in terminal output next to each finding
- `name` — human-readable label
- `description` — justification for the threshold (used in the report)
- `predicate` — a `Callable[[Finding], bool]`; can match on `cwe`, `severity`, `tool`, `message`, or any combination
- `verdict` — `Verdict.BLOCK`, `Verdict.WARN`, or `Verdict.ALLOW`

Write a test for every new rule in `tests/policy/test_rules.py`.

---

## Adding a new command

Add the command function to `all_cli_commands` in `commands/__init__.py`. The function is automatically registered as a subcommand of the main Click group.

If installed in editable mode, it is available immediately: `gatekeeper new-command`.

---

## Docker image

The image is built from `docker/Dockerfile`. It installs tools at build time via `docker_install_tools_image_step.py`, which reads `tools-config.yaml` and runs each `installation_command`.

At scan time, `docker_scan_command_entrypoint.py` is the container entry point. It filters tools by name, runs them in parallel threads, and aggregates output.

**Rebuild the image when you change:**
- `docker/Dockerfile`
- `docker/docker_scan_command_entrypoint.py`
- `docker/docker_install_tools_image_step.py`
- `tools-config.yaml`

```bash
docker build --no-cache -f docker/Dockerfile -t gatekeeper-scanner .
```

---

## Running the tests

```bash
uv run pytest tests/policy -v
```

28 tests cover: `Verdict` precedence, `PolicyEngine` behaviour, and all 8 default rules (positive and negative cases). No Docker required.

To add tests for a new rule, add parametrize cases to `tests/policy/test_rules.py`.

---

## Logging and exceptions

Use `cli_log` from `utils/printer.py` — do not use `print()` or the standard `logging` module.

```python
from gatekeeper.utils.printer import LogLevel, cli_log

cli_log("Something happened", LogLevel.INFO)
cli_log("Something went wrong", LogLevel.ERROR)
```

Use `CliException` for user-facing errors that should not leak a stack trace:

```python
from gatekeeper.utils.printer import CliException
raise CliException("Docker is not running.")
```

Use `click.style(...)` for coloured output inside log messages:

```python
cli_log(click.style("Scan complete", fg="green", bold=True))
```

---

## Code quality

Configured in `pyproject.toml`. Run before committing:

```bash
uv run black src/
uv run isort src/
uv run flake8 src/
uv run mypy src/
```
