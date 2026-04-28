# Improvements & Known Gaps

## SAST Tool Coverage

- [x] **Add missing language-specific tools** — the following tools are documented in the README but not yet configured in `tools-config.yaml`:
  - [x] ESLint + `eslint-plugin-security` (JavaScript / TypeScript)
  - [x] SpotBugs + FindSecBugs plugin (Java) — best-effort; requires `pom.xml` in repo root
  - [x] Flawfinder (C / C++)
  - [x] Progpilot (PHP)
- [x] **Fix gosec `supported_file_extensions`** — was commented out in `tools-config.yaml`; now uncommented so gosec only runs when `.go` files are present

---

## Scanning Behaviour

- [ ] **Scan only changed files** — the pre-commit hook currently scans the whole repository on every commit; it should ideally only scan files (or diffs) that are part of the staged changes
- [ ] **Exclude irrelevant directories** — directories like `.venv`, `node_modules`, `dist`, and `build` are currently included in scans; if changed-files scanning is not implemented, these should at least be explicitly excluded

---

## Findings & Policy

- [x] **Unified findings parser** — `src/gatekeeper/utils/findings_parser.py` normalises each tool's raw JSON into a common `Finding` schema (tool, file, line, severity, message)
- [x] **Python policy engine** — `src/gatekeeper/utils/policy.py` evaluates parsed findings against rules in `tools-config.yaml` (`policy:` block) and causes `gatekeeper scan` to exit non-zero when violations are found, blocking the pre-commit hook

---

## Configuration & UX

- [ ] **More user configuration** — expose additional options to the user (e.g. which tools to enable/disable, severity thresholds, exclude patterns) without requiring edits to internal files

---

## Extensions (pick one to implement)

- [x] **HTML Dashboard** — `src/gatekeeper/utils/dashboard.py` generates a self-contained `report.html` in `.gatekeeper/` after every scan, showing a severity breakdown and colour-coded findings table; violations are highlighted; pass `--no-report` to skip
- [ ] Waiver system — allow teams to acknowledge and suppress specific findings with an audit trail
- [ ] CI/CD integration — provide a ready-to-use configuration for running Gatekeeper in GitHub Actions / GitLab CI
- [ ] LLM explanation — use a language model to explain findings in plain language and suggest fixes
