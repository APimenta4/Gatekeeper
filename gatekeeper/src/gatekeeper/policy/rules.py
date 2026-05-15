from gatekeeper.parsers.model import (
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
)
from gatekeeper.policy.rule import Rule
from gatekeeper.policy.verdict import Verdict

default_rules: list[Rule] = [
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
    Rule(
        id="GK-002",
        name="SQL Injection (High / Critical)",
        description=(
            "CWE-89: SQL injection at HIGH or CRITICAL severity indicates a directly "
            "exploitable query construction pattern. Blocked to prevent data exfiltration "
            "and authentication bypass."
        ),
        predicate=lambda f: f.cwe == "CWE-89" and f.severity in (SEVERITY_HIGH, SEVERITY_CRITICAL),
        verdict=Verdict.BLOCK,
    ),
    Rule(
        id="GK-003",
        name="SQL Injection (Medium)",
        description=(
            "CWE-89: SQL injection at MEDIUM severity is likely exploitable under specific "
            "conditions. Warned rather than blocked to allow teams to assess context, but "
            "must be reviewed before merging to main."
        ),
        predicate=lambda f: f.cwe == "CWE-89" and f.severity == SEVERITY_MEDIUM,
        verdict=Verdict.WARN,
    ),
    Rule(
        id="GK-004",
        name="Path Traversal",
        description=(
            "CWE-22: Improper path neutralisation allows attackers to read or write "
            "arbitrary files on the server. Blocked unconditionally because the attack "
            "surface is the entire filesystem."
        ),
        predicate=lambda f: f.cwe == "CWE-22",
        verdict=Verdict.WARN,
    ),
    Rule(
        id="GK-005",
        name="Hardcoded Credentials",
        description=(
            "CWE-798 / CWE-259: Hard-coded passwords or API keys committed to source "
            "control are permanently compromised once the repository is cloned. Blocked "
            "to enforce secrets management practices."
        ),
        predicate=lambda f: f.cwe in ("CWE-798", "CWE-259"),
        verdict=Verdict.BLOCK,
    ),
    Rule(
        id="GK-006",
        name="Insecure Deserialization",
        description=(
            "CWE-502: Deserialising untrusted data (e.g. pickle.load, yaml.load without "
            "Loader) can lead to arbitrary code execution. Blocked because the exploit "
            "requires no authentication in most web contexts."
        ),
        predicate=lambda f: f.cwe == "CWE-502",
        verdict=Verdict.BLOCK,
    ),
    Rule(
        id="GK-007",
        name="Cross-Site Scripting",
        description=(
            "CWE-79: Reflected or stored XSS lets attackers execute scripts in a victim's "
            "browser. Warned rather than blocked because context (output encoding, framework "
            "escaping) determines actual exploitability."
        ),
        predicate=lambda f: f.cwe == "CWE-79",
        verdict=Verdict.WARN,
    ),
    Rule(
        id="GK-008",
        name="Weak Cryptography",
        description=(
            "CWE-327: Use of broken or risky cryptographic algorithms (MD5, SHA-1, DES, RC4) "
            "makes encrypted data vulnerable to brute-force or known-plaintext attacks. "
            "Warned to prompt migration to modern algorithms without hard-blocking."
        ),
        predicate=lambda f: f.cwe == "CWE-327",
        verdict=Verdict.WARN,
    ),
]
