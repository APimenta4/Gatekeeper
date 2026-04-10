import subprocess
from pathlib import Path

import click
import yaml

from gatekeeper.utils.git import get_git_root_path, raise_if_in_not_git_repository
from gatekeeper.utils.printer import CliException, LogLevel, cli_log


def setup() -> None:
    """Sets up the current repository by installing the pre-commit hook"""
    raise_if_in_not_git_repository()
    _setup_gatekeeper_precommit_hook()
    cli_log(
        click.style(
            "Gatekeeper pre-commit hook installed successfully!", fg="green", bold=True
        )
    )


def _setup_gatekeeper_precommit_hook() -> None:
    cli_log("Setting up Gatekeeper pre-commit hook...")
    _create_precommit_config()
    _run_precommit_install()


def _create_precommit_config() -> None:
    git_root_path = get_git_root_path()
    config_path = Path(git_root_path) / ".pre-commit-config.yaml"

    gatekeeper_hook = {
        "id": "gatekeeper",
        "name": "Gatekeeper Security Scanner",
        "entry": "gatekeeper scan",
        "language": "system",
        "stages": ["commit"],
    }

    if config_path.exists():
        cli_log(
            f"Found existing {click.style('.pre-commit-config.yaml', fg='green', bold=True)} file, "
            f"appending gatekeeper hook..."
        )
        config = yaml.safe_load(config_path.read_text()) or {}
        repos = config.get("repos", [])

        local_repo = None
        for repo in repos:
            if repo.get("repo") == "local":
                local_repo = repo
                break

        if local_repo is None:
            local_repo = {"repo": "local", "hooks": []}
            repos.append(local_repo)

        hooks = local_repo.get("hooks", [])
        if any(hook.get("id") == "gatekeeper" for hook in hooks):
            raise CliException(
                "Gatekeeper hook already exists in .pre-commit-config.yaml"
            )

        hooks.append(gatekeeper_hook)
        config["repos"] = repos
        config_path.write_text(yaml.dump(config))
    else:
        cli_log(
            f"Creating {click.style('.pre-commit-config.yaml', fg='green', bold=True)} file..."
        )
        config = {"repos": [{"repo": "local", "hooks": [gatekeeper_hook]}]}
        config_path.write_text(yaml.dump(config))


def _run_precommit_install() -> None:
    cli_log("Installing hook...")
    try:
        subprocess.run(["pre-commit", "install"], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        cli_log(
            f"Failed to install pre-commit hooks: {e.stderr.decode()}",
            LogLevel.ERROR,
        )
