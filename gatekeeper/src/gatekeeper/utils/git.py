import subprocess

import click


def raise_if_in_not_git_repository() -> None:
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise click.ClickException(
            "You are not currently inside a git repository. "
            "Gatekeeper relies on pre-commit hooks and therefore needs to be in a git repository to function."
        ) from e
