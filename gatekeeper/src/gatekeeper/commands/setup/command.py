from gatekeeper.utils.git import raise_if_in_not_git_repository
from gatekeeper.utils.printer import cli_print


def setup() -> None:
    raise_if_in_not_git_repository()
    cli_print("Installing Gatekeeper pre-commit hook...")
