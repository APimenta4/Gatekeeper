import subprocess
import sys
from pathlib import Path

import click
import yaml

from gatekeeper.utils.git import get_git_root_path, raise_if_in_not_git_repository
from gatekeeper.utils.printer import LogLevel, cli_log


def setup() -> None:
    """Sets up the current repository by installing the pre-commit hook"""
    raise_if_in_not_git_repository()
    _setup_gatekeeper_precommit_hook()


def _setup_gatekeeper_precommit_hook() -> None:
    cli_log("Setting up Gatekeeper pre-commit hook...")
    _create_precommit_config()
    _run_precommit_install()


def _create_precommit_config() -> None:
    git_root_path = get_git_root_path()
    precommit_file_path = Path(git_root_path) / ".pre-commit-config.yaml"

    gatekeeper_hook = {
        "id": "gatekeeper",
        "name": "Gatekeeper Security Scanner",
        "entry": "gatekeeper scan",
        "language": "system",
        "stages": ["commit"],
    }

    if precommit_file_path.exists():
        cli_log(
            f"Found existing {click.style('.pre-commit-config.yaml', fg='green', bold=True)} file, "
            f"appending gatekeeper hook..."
        )
        config = yaml.safe_load(precommit_file_path.read_text()) or {}
        repos = config.get("repos", [])

        local_repo = (
            None  # if local repo already exists, we append gatekeeper as a hook
        )
        for repo in repos:
            if repo.get("repo") == "local":
                local_repo = repo
                break

        if local_repo is None:
            local_repo = {"repo": "local", "hooks": []}
            repos.append(local_repo)

        hooks = local_repo.get("hooks", [])
        if any(hook.get("id") == "gatekeeper" for hook in hooks):
            cli_log(
                f"Gatekeeper hook already exists in {click.style('.pre-commit-config.yaml', fg='green', bold=True)} "
                f"file, attempting to reinstall...",
                LogLevel.WARNING,
            )
            _run_precommit_install(True)
            exit(0)

        hooks.append(gatekeeper_hook)
        config["repos"] = repos
        precommit_file_path.write_text(yaml.dump(config))
    else:
        cli_log(
            f"Creating {click.style('.pre-commit-config.yaml', fg='green', bold=True)} file..."
        )
        config = {"repos": [{"repo": "local", "hooks": [gatekeeper_hook]}]}
        precommit_file_path.write_text(yaml.dump(config))


def _run_precommit_install(reinstalling: bool = False) -> None:
    cli_log("Installing hook...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pre_commit", "install"],
            check=True,
            capture_output=True,
        )
        cli_log(
            click.style(
                (
                    "Gatekeeper pre-commit hook reinstalled successfully!"
                    if reinstalling
                    else "Gatekeeper pre-commit hook installed successfully!"
                ),
                fg="green",
                bold=True,
            )
        )

    except subprocess.CalledProcessError as e:
        cli_log(
            f"Failed to install pre-commit hooks: {e.stderr.decode()}",
            LogLevel.ERROR,
        )
