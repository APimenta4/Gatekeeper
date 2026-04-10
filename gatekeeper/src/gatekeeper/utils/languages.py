from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    JAVA = "Java"
    GO = "Go"
    CPP = "C++"
    C = "C"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class LanguageConfig:
    """Extensible language-specific configuration"""

    file_extensions: set[str]


LANGUAGES_CONFIG = {
    Language.PYTHON: LanguageConfig(
        file_extensions={".py"},
    ),
    Language.JAVASCRIPT: LanguageConfig(
        file_extensions={".js", ".jsx"},
    ),
    Language.TYPESCRIPT: LanguageConfig(
        file_extensions={".ts", ".tsx"},
    ),
    Language.JAVA: LanguageConfig(
        file_extensions={".java"},
    ),
    Language.GO: LanguageConfig(
        file_extensions={".go"},
    ),
    Language.CPP: LanguageConfig(
        file_extensions={".cpp"},
    ),
    Language.C: LanguageConfig(
        file_extensions={".c"},
    ),
}
