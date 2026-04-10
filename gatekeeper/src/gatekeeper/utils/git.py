import subprocess

from gatekeeper.utils.printer import CliException, LogLevel, cli_log


def raise_if_in_not_git_repository() -> None:
    cli_log("Detecting git repository...", LogLevel.INFO)
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise CliException(
            "Not a git repository. Please run this command in a git repository."
        )


def get_git_root_path() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise CliException("Failed to retrieve git repository root.")


def get_git_tracked_files_current_dir() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            check=True,
            text=True,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise CliException("Failed to retrieve git-tracked files.")
