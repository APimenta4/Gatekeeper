from dataclasses import dataclass


@dataclass(frozen=True)
class SastTool:
    """Represents a generic SAST tool that will be run on any codebase,
    regardless of the programming languages used."""

    name: str
    # Commands to be used in the docker engine to install and run the tool
    tool_installation_command: str
    tool_execution_command: str


@dataclass(frozen=True)
class SpecificSastTool(SastTool):
    """Represents a SAST tool that will only be run if certain
    programming languages are detected in the codebase."""

    supported_file_extensions: frozenset[str]


GENERIC_SAST_TOOLS = {
    SastTool(
        name="Semgrep",
        tool_installation_command="pip install semgrep",
        tool_execution_command="semgrep --config=auto --json --output {output_file}",
    ),
    SastTool(
        name="Trivy",
        tool_installation_command="apt install trivy",
        tool_execution_command="trivy fs --format json --output {output_file} .",
    ),
}

SPECIFIC_SAST_TOOLS = {
    SpecificSastTool(
        name="Bandit",
        tool_installation_command="pip install bandit",
        tool_execution_command="bandit -r . -f json -o {output_file}",
        supported_file_extensions=frozenset({".py"}),
    ),
}

ALL_SAST_TOOLS = GENERIC_SAST_TOOLS.union(SPECIFIC_SAST_TOOLS)

# to be added:
# Language.JAVASCRIPT: LanguageConfig(
#         file_extensions={".js", ".jsx"},
#     ),
#     Language.TYPESCRIPT: LanguageConfig(
#         file_extensions={".ts", ".tsx"},
#     ),
#     Language.JAVA: LanguageConfig(
#         file_extensions={".java"},
#     ),
#     Language.GO: LanguageConfig(
#         file_extensions={".go"},
#     ),
#     Language.CPP: LanguageConfig(
#         file_extensions={".cpp"},
#     ),
#     Language.C: LanguageConfig(
#         file_extensions={".c"},
#     ),
