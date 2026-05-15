import subprocess
import sys
from pathlib import Path

import click
import yaml

from gatekeeper.utils.git import get_git_root_path, raise_if_in_not_git_repository
from gatekeeper.utils.printer import LogLevel, cli_log


@click.option(
    "--details/--no-details",
    default=True,
    show_default=True,
    help="Include per-finding messages in the pre-commit hook output",
)
def setup(details: bool) -> None:
    """Sets up the current repository by installing the pre-commit hook"""
    raise_if_in_not_git_repository()
    _setup_gatekeeper_precommit_hook(details=details)


def _setup_gatekeeper_precommit_hook(*, details: bool) -> None:
    cli_log("Setting up Gatekeeper pre-commit hook...")
    _create_precommit_config(details=details)
    _run_precommit_install()


def _create_precommit_config(*, details: bool) -> None:
    git_root_path = get_git_root_path()
    precommit_file_path = Path(git_root_path) / ".pre-commit-config.yaml"

    entry = "gatekeeper scan" if details else "gatekeeper scan --no-details"

    gatekeeper_hook = {
        "id": "gatekeeper",
        "name": "Gatekeeper Security Scanner",
        "entry": entry,
        "language": "system",
        "stages": ["pre-commit"],
        "pass_filenames": False,
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
        existing_hook = next((hook for hook in hooks if hook.get("id") == "gatekeeper"), None)
        if existing_hook is not None:
            existing_hook["entry"] = entry
            config["repos"] = repos
            precommit_file_path.write_text(yaml.dump(config))
            cli_log(
                f"Gatekeeper hook already exists in {click.style('.pre-commit-config.yaml', fg='green', bold=True)} "
                f"file, updated its entry and attempting to reinstall...",
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
