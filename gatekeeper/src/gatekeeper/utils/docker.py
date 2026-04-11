import subprocess

from gatekeeper.utils.printer import CliException


def raise_if_docker_not_running() -> None:
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        raise CliException(
            "Docker does not seem to be running. Please ensure Docker is running before trying to use this command."
        )
