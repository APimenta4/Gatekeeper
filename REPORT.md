# MESW SES 2025/2026

## Security Gatekeeper Evaluation Report

This project was developed by Group 3:

| Name                                        | Student ID |
| ------------------------------------------- | ---------- |
| Afonso da Cruz Pimenta                      | 202502507  |
| Gonçalo Araújo Guimarães Cardoso Sampaio    | 202206636  |
| Gonçalo de Almeida Pinto e Morais de Castro | 202007851  |
| José Pedro Pereira da Costa                 | 202207871  |

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

Analyses the files tracked by Git and selects the appropriate SAST tools based on the file extensions found in the repository. Generic tools such as [_Semgrep_](https://github.com/semgrep/semgrep) and [_Trivy_](https://github.com/aquasecurity/trivy) are always selected, while language-specific tools such as [_Bandit_](https://github.com/pycqa/bandit), [_gosec_](https://github.com/securego/gosec), [_ESLint_](https://github.com/eslint/eslint), [_SpotBugs_](https://github.com/spotbugs/spotbugs), [_Flawfinder_](https://github.com/david-a-wheeler/flawfinder), and [_Progpilot_](https://github.com/designsecurity/progpilot) are selected only when matching source files are detected.

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

```Python
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

The possible verdicts are `ALLOW`, `WARN`, and `BLOCK`, with the last having the highest precedence when multiple rules match the same finding. The current rules cover the following vulnerabilities:

- **Command Injection**
- **SQL Injection**
- **Path traversal**
- **Hardcoded Credentials**
- **Insecure Deserialization**
- **Cross-Site Scripting**
- **Weak cryptography**.

Findings classified as `BLOCK` cause the _scan_ command to exit with a non-zero status code, which prevents the commit from completing when Gatekeeper runs as a pre-commit hook.

##### 2.2.5 Reporting Stage

Finally, Gatekeeper generates developer-facing feedback which groups findings by policy decision and displays blocked issues, warnings, allowed findings, affected files, line numbers, CWEs, and a final result. In addition to the terminal output, the tool can generate an HTML dashboard in the _.gatekeeper_ directory, summarizing the findings by severity and listing detailed results with filters for severity, file extension, and CWE.

### 3. Policy Decisions

### 4. Evaluation Methodology

### 5. Results and FP/FN Analysis

### 6. Developer Experience and Performance

### 7. Lessons Learned and Limitations

### 8. Demo

### 9. Conclusion
