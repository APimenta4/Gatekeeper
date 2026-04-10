from gatekeeper.utils.git import raise_if_in_not_git_repository
from gatekeeper.utils.languages import LANGUAGES_CONFIG, Language
from gatekeeper.utils.printer import cli_print


def scan() -> None:
    raise_if_in_not_git_repository()

    source_code_languages = _detect_source_code_languages()

    # invoke_logging_docker_scan_engine(source_code_languages, LOG_FILE_PATH)

    # do_things_with_log_file_like_print

    # delete_log_file()

    cli_print("Running Gatekeeper scan...")


def _detect_source_code_languages() -> set[Language]:
    files = []

    file_extensions = set()
    for file in files:
        # for file in files if file not in IGNORED_FILES:
        # check file.suffix
        _, ext = file.rsplit(
            ".", 1
        )  # can this throw error if file does not have .? try catch and ignore ig
        file_extensions.add(f".{ext}")

    source_code_languages = set()

    for language, config in LANGUAGES_CONFIG.items():
        if config.file_extensions.intersection(file_extensions):
            source_code_languages.add(language)

    return source_code_languages
