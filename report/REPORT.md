# MESW SES 2025/2026

## Security Gatekeeper Evaluation Report

This project was developed by Group 3:

| Name                                        | Student Number |
| ------------------------------------------- | -------------: |
| Afonso da Cruz Pimenta                      |      202502507 |
| Gonçalo Araújo Guimarães Cardoso Sampaio    |      202206636 |
| Gonçalo de Almeida Pinto e Morais de Castro |      202007851 |
| José Pedro Pereira da Costa                 |      202207871 |

### 1. Introduction and Goal

Gatekeeper is a developer-facing security CLI tool designed to make **Static Application Security Testing** (SAST) easier to run during development. This tool allows multiple security tools to be executed through a single, user-friendly command. Gatekeeper can also be integrated directly into the Git commit workflow through a pre-commit hook, allowing vulnerabilities to be detected before code is committed. Depending on the configured security policy, certain findings can block the commit, preventing vulnerable code from being pushed to GitHub or reaching later stages of the development pipeline.

The tool is designed to be extensible and customizable, allowing users to configure which analysers should run and how they should be executed. To avoid polluting the developer's local environment with multiple independent tool installations, Gatekeeper runs the scanning process inside a Docker-based environment.

This report evaluates Gatekeeper as a local security gate by analysing its design, detection results (including false positive and false negative findings), scan performance, and developer feedback on its usability.

### 2. Design and Implementation

The system is structured around two main layers:

- a Python CLI (implemented with [**_click_**](https://click.palletsprojects.com/en/stable/));
- a Docker-based scanning engine.

#### 2.1 CLI commands

- **`scan`**: runs the security scanning pipeline on the current repository by selecting the appropriate SAST tools, starting the Docker-based scanning engine, collecting the generated results, applying the policy rules, and printing the final security report.

- **`setup`**: installs Gatekeeper into the current Git repository by creating or updating the `.pre-commit-config.yaml` file and registering a local pre-commit hook that runs `gatekeeper scan` automatically before each commit.

#### 2.2 Vulnerability Scanning Process

The scan process follows a pipeline-based architecture where a shared `ScanContext` object is passed through a sequence of filters each responsible for one stage of the scan:

##### 2.2.1 Tool Selection Stage

At this stage, the tool analyses the files tracked by Git and selects the appropriate SAST tools based on the file extensions found in the repository. Generic tools such as [_Semgrep_](https://github.com/semgrep/semgrep) and [_Trivy_](https://github.com/aquasecurity/trivy) are always selected, while language-specific tools such as [_Bandit_](https://github.com/pycqa/bandit), [_gosec_](https://github.com/securego/gosec), [_ESLint_](https://github.com/eslint/eslint), [_SpotBugs_](https://github.com/spotbugs/spotbugs), [_Flawfinder_](https://github.com/david-a-wheeler/flawfinder), and [_Progpilot_](https://github.com/designsecurity/progpilot) are selected only when matching source files are detected.

##### 2.2.2 Docker Execution Stage

The target repository is mounted into the container, and the selected tools are passed as arguments to the container entrypoint. Inside the container, each selected tool is executed and produces an individual _JSON_ output file. These results are then aggregated into a single _findings.json_ file inside the repository's _.gatekeeper_ directory, allowing the host CLI to continue processing the results after the container finishes.

##### 2.2.3 Findings Normalization

Since each scanner produces a different output format, Gatekeeper includes a parser layer that normalizes tool-specific _JSON_ results into a common finding model that stores:

- the **tool** that produced it;
- the **affected file**;
- the **line number**;
- its **severity**;
- a **message**;
- the **CWE identifier** (if available).

Finding example:

```Python
Finding(
    tool="Semgrep",
    file=".github/workflows/docker-image.yml",
    line=29,
    severity="HIGH",
    message="Using variable interpolation with github context data in a run step could allow command injection.",
    cwe="CWE-78",
)
```

This normalized representation allows later stages of the pipeline to evaluate findings consistently, regardless of which tool detected them.

##### 2.2.4 Policy Evaluation

The policy engine is implemented in Python and evaluates each normalized finding against a set of predefined rules that contain:

- an **identifier**;
- a **name**;
- a **description**;
- a **predicate**;
- a **final verdict**.

Rule example:

```python
Rule(
    id="GK-001",
    name="Command Injection",
    description=(
        "CWE-78: OS command injection allows attackers to execute arbitrary "
        "shell commands. Blocked unconditionally regardless of severity because "
        "even low-rated findings represent a critical risk in production systems."
    ),
    predicate=lambda f: f.cwe == "CWE-78",
    verdict=Verdict.BLOCK,
),
```

##### 2.2.5 Reporting Stage

Finally, Gatekeeper generates developer-facing feedback which groups findings by policy decision and displays blocked issues, warnings, allowed findings, affected files, line numbers, CWEs, and a final result. In addition to the terminal output, the tool can generate an HTML dashboard (our selected extension) in the _.gatekeeper_ directory, summarizing the findings by severity and listing detailed results with filters for severity, file extension, and CWE.

### 3. Policy Decisions

The policy engine was designed to transform raw security findings into actionable decisions for developers. Instead of treating all findings equally, the tool classifies them into three possible verdicts: `ALLOW`, `WARN`, and `BLOCK`. This distinction is important because security tools often produce noisy results, and blocking every finding would make the tool frustrating to use in a real development workflow.

`BLOCK`: used for vulnerabilities that represent a direct and high-impact security risk, especially when exploitation could lead to command execution, credential leakage, arbitrary file access, or remote code execution. These findings cause the scan to exit with a non-zero status code and prevent the commit from completing when Gatekeeper is used as a pre-commit hook.

`WARN`: used for findings that are security-relevant but may require additional context before being considered exploitable. These findings are still shown to the developer, but they do not block the commit. They make the tool provide useful feedback without introducing excessive friction.

`ALLOW`: used when no policy rule matches a finding. In this case, the finding is still recorded, but it is not considered severe enough by the current policy to warn or block the developer.

The selected policy rules were not chosen only because they are generally important security categories, they were defined according to two practical constraints: 

- Matching the type of findings that the integrated tools are actually able to report: the policy engine was designed around CWEs that can realistically appear in the normalized findings.

- The policies had to be verifiable against the evaluation target that focus on CWEs that could be exercised and evaluated using the target application. The overlap with OWASP Top 10 categories is a consequence of these choices, since many of the vulnerabilities detected by the tools and present in DVWA also belong to common web application risk categories.

| Rule   | Vulnerability            | Condition                             | Verdict | Rationale                                                                                                                                   |
| ------ | ------------------------ | ------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| GK-001 | Command Injection        | CWE-78                                | BLOCK   | Allows arbitrary shell command execution, which is considered critical even if the scanner assigns a lower severity.                        |
| GK-002 | SQL Injection            | CWE-89 with HIGH or CRITICAL severity | BLOCK   | May allow data exfiltration, authentication bypass, or database manipulation.                                                               |
| GK-003 | SQL Injection            | CWE-89 with MEDIUM severity           | WARN    | Potentially dangerous, but exploitability may depend on context and query construction.                                                     |
| GK-004 | Path Traversal           | CWE-22                                | WARN    | May allow attackers to read or write arbitrary files, but exploitability often depends on how user-controlled paths are validated and used. |
| GK-005 | Hardcoded Credentials    | CWE-798 or CWE-259                    | BLOCK   | Secrets committed to source control should be considered compromised.                                                                       |
| GK-006 | Insecure Deserialization | CWE-502                               | BLOCK   | Can lead to arbitrary code execution when untrusted data is deserialized.                                                                   |
| GK-007 | Cross-Site Scripting     | CWE-79                                | WARN    | XSS exploitability depends on output encoding, framework protections, and execution context.                                                |
| GK-008 | Weak Cryptography        | CWE-327                               | WARN    | Weak algorithms should be replaced, but they may not always represent an immediately exploitable vulnerability.                             |

### 4. Evaluation Methodology

The evaluation was designed to assess Gatekeeper in terms of security effectiveness, performance, and developer experience.

#### 4.1 Target Application

For this evaluation, Gatekeeper was executed against the **[_DVWA_ (Damn Vulnerable Web Application)](https://github.com/digininja/DVWA/)** repository. This target contains known vulnerability patterns, making it suitable for evaluating whether Gatekeeper can detect real security issues in a realistic codebase.

#### 4.2 Security Effectiveness

The generated findings were manually reviewed to determine whether they corresponded to real vulnerabilities in the target application and were classified as one of the following:

- **True Positive (TP)**: a real vulnerability correctly detected by Gatekeeper;
- **False Positive (FP)**: a reported finding that does not correspond to a real vulnerability;
- **False Negative (FN)**: a real vulnerability that exists in the tested repository but was not detected by the tool.

Based on this classification, we measured precision, false positive rate, false negative rate, and CWE coverage.

#### 4.3 Policy Evaluation

Besides checking whether Gatekeeper detected real vulnerabilities, we also evaluated whether the policy engine assigned an appropriate decision to each finding because Gatekeeper is not only expected to report issues, but also to decide whether they should block the commit, generate a warning, or be allowed.

For every detected issue, we recorded the vulnerability type, CWE identifier, severity, detecting tool, Gatekeeper verdict (`ALLOW`, `WARN`, or `BLOCK`), and whether the decision was appropriate.

#### 4.4 Performance Evaluation

Performance was measured by recording the total scan time on the _DVWA_ repository and comparing it with the project requirement of completing a scan in under 30 seconds on a medium-sized project.

#### 4.5 Developer Experience

DX was evaluated by asking 3 different developers to test the tool, inspect the terminal report and rate its clarity, as well as whether the output provided enough information to understand what needed to be fixed.

> The HTML report was also considered part of the developer experience evaluation because it was implemented as a project extension to improve the visualization of the generated scan data and it aims to make security results easier to visualize.

### 5. Results and FP/FN Analysis

The full raw generated outputs and the HTML report used for the _DVWA_ evaluation are available in [`report/dvwa-evaluation/`](report/dvwa-evaluation/).

> The repository was scanned on the 8th of June, 2026.

#### 5.1 Scan Summary

Gatekeeper reported a total of 76 findings when scanning the _DVWA_ repository and no critical findings were reported. Out of all findings, (approximately) a third were classified as policy violations, meaning that they matched blocking policy rules and caused the scan to fail.

A policy violation does not simply mean that the scanner reported an issue but that the finding matched one of Gatekeeper's blocking policy rules, causing the scan to fail and preventing the commit from completing when executed through the pre-commit hook.

| Metric            | Value |
| ----------------- | ----: |
| Total findings    |    76 |
| Critical findings |     0 |
| High findings     |    45 |
| Medium findings   |    27 |
| Low findings      |     4 |
| Policy violations |    26 |

#### 5.2 Gatekeeper Findings Classification

<!-- Detection: ✅ Correct (TP) / ❌ False Positive / Negative -->

| Finding | Real vulnerability? | Gatekeeper decision | Detection |
|-|:-:|:-:|:-:|
| **CWE-78** in `.github/workflows/docker-image.yml` | Yes | ⛔ Blocked | FP / TP |
| **CWE-697** in `login.php` | Yes | 🆗 Allowed | FP / TP |
| **CWE-200** in `phpinfo.php` | Yes | 🆗 Allowed | FP / TP |
| **CWE-94** in  `vulnerabilities/api/src/HealthController.php` | Yes | 🆗 Allowed | FP / TP |

#### 5.3 Metrics
WIP

### 6. Developer Experience (Performance & Peer Evaluation) 

Gatekeeper was evaluated not only in terms of security detection, but also in terms of its usability in a developer workflow. Since the tool is intended to run locally and as part of a pre-commit hook, it must provide useful feedback without introducing excessive delay or friction.

#### 6.1 Performance

Performance was evaluated by observing the time required to complete scans in different development environments. In the main evaluation scenario, Gatekeeper was able to complete the scan within the target threshold of 30 seconds, showing that the tool can provide fast feedback when used as part of a local development workflow.

As expected, however, the scan time is not constant and depends on several factors such as the size of the repository, the enabled security tools, the machine's hardware, the operating system, and the local development/Docker execution environments.

Overall, the results show that Gatekeeper can be effectively used as a local security gate, providing timely feedback before code is committed. For projects where scan time becomes more significant, the tool can still remain practical by adjusting the enabled scanners or by separating quick pre-commit checks from more complete scans executed manually or later in the development pipeline.

#### 6.2 Peer Evaluation

To evaluate Gatekeeper from a developer experience perspective, three peers were asked to test the tool and analyse its output. The goal was to understand whether the tool would be usable in a real development workflow, especially when executed as a local scan or as part of a pre-commit process. The evaluation also aimed to identify possible improvements, missing features, and changes that could make the tool more useful for developers.

**Peer 1: Informatics and Computing Engineering Bachelor's Student**
- **Context**: Tested on an academic web project developed with HTML, PHP, and JavaScript. 
- **Feedback**: Considered the tool useful for the tested project and for future development projects. 
- **Observations**: Highlighted the HTML report as a more visual and accessible way to inspect results. 
- **Suggestions**: Adding remediation guidance, with code correction suggestions for each detected issue.

**Peer 2: Informatics and Computing Engineering Master's Student**
- **Context**: Tested on a web application developed with Laravel and JavaScript. 
- **Feedback**: Considered the tool interesting and useful, because it combines multiple scanners into a single workflow and translates raw findings into clearer policy decisions.
- **Observations**: Highlighted that the CWE information was useful, but sometimes too generic. 
- **Suggestions**: The explanation of each CWE should be more specific to the affected code; Adding a code correction mode to the tool (similar to a coding agent, that fixes the affected files).

**Peer 3: Software Developer with Team Project Experience**
- **Context**: Tested from the perspective of a developer working in a collaborative project environment, where multiple team members may be committing code in parallel.
- **Feedback**: Considered the tool useful, especially when used on demand to inspect the security state of a project before pushing changes or before merging work into shared branches.
- **Observations**: Blocking every commit that matches a BLOCK policy could slow down development, especially in team workflows where developers may be working on independent features or temporary branches.
- **Suggestions**: Integrating Gatekeeper into a CI/CD workflow, where security checks would run automatically before merging into protected branches which would allow the tool to enforce security policies at important integration points, while still giving developers flexibility during local development.

### 7. Lessons Learned and Limitations
WIP
- **False Positives with Naive Scanners**: Some underlying SAST tools rely on simple pattern matching, leading to false positives. We learned that tuning the policy engine to handle these cases requires careful rule creation, potentially using more advanced context-aware filters.
- **Docker Overhead**: While using Docker ensures a clean environment, it introduces a small startup overhead. However, maintaining the sub-30s execution time proved this trade-off is worthwhile for the benefit of avoiding local dependency problems.
- **Extensibility**: The Python-based policy engine proved highly extensible. Writing custom lambda-based rules is very developer-friendly compared to complex YAML configurations.

### 8. Conclusion
WIP
Gatekeeper successfully meets its goal of serving as an effective, developer-friendly local security gate. By integrating directly into the Git workflow and utilizing a containerized scanning engine with an extensible Python policy layer, it provides immediate security feedback. While false positives and false negatives still exist, inherent to the underlying SAST tools, the custom policy engine mitigates noise by categorizing findings into actionable verdicts. Overall, the tool enhances developer experience and prevents critical vulnerabilities from reaching the main codebase.
