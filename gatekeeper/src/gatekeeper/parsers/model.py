from dataclasses import dataclass

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


@dataclass
class Finding:
    tool: str
    file: str
    line: int
    severity: str
    message: str
