import subprocess
from datetime import datetime
from pathlib import Path
from time import sleep

import click
from halo import Halo

from gatekeeper.defaults import SCAN_ENGINE_FINDINGS_FILE_NAME
from gatekeeper.pipeline.base import ScanFilter
from gatekeeper.pipeline.context import ScanContext
from gatekeeper.utils.printer import CliException, cli_log


class DockerScanFilter(ScanFilter):
    def process(self, ctx: ScanContext) -> ScanContext:
        ctx.findings_file_path = str(
            ctx.git_root / ".gatekeeper" / SCAN_ENGINE_FINDINGS_FILE_NAME
        )
        container_output = f"/repo/.gatekeeper/{SCAN_ENGINE_FINDINGS_FILE_NAME}"
        tool_names = ",".join(t.name for t in ctx.sast_tools)

        cli_log("Starting scanning docker engine...")

        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{ctx.git_root}:/repo",
            "gatekeeper-scanner",
            "--tools", tool_names,
            "--output", container_output,
        ]

        if ctx.verbose:
            cli_log("Attaching engine's container shell...")
            sleep(2)
        else:
            docker_cmd.insert(3, "--quiet")
            cli_log("Running engine in quiet mode...")

        try:
            if ctx.verbose:
                subprocess.run(docker_cmd, check=True, stdout=None, stderr=None)
            else:
                _run_with_spinner(docker_cmd)
        except subprocess.CalledProcessError as e:
            raise CliException(f"Error occurred while running the scanning engine: {e}")

        return ctx


def _run_with_spinner(docker_cmd: list[str]) -> None:
    start_time = datetime.now()
    prefix = (
        click.style(f"[{datetime.now().strftime('%H:%M:%S')}] ", fg="green")
        + click.style("[Gatekeeper] ", fg="cyan", bold=True)
        + click.style("[INFO] ", fg="green", bold=True)
    )
    spinner = Halo(
        text=prefix + click.style("Scanning repository", fg="green", bold=True),
        spinner="dots",
        placement="right",
    )
    spinner.start()

    process = subprocess.Popen(docker_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while process.poll() is None:
        elapsed = (datetime.now() - start_time).seconds
        spinner.text = (
            prefix
            + click.style("Scanning repository", fg="green", bold=True)
            + click.style(f" {elapsed} seconds elapsed", fg="yellow")
        )
        sleep(1)

    elapsed_total = (datetime.now() - start_time).seconds
    if process.returncode == 0:
        spinner.succeed(prefix + click.style("Done", fg="green", bold=True) + click.style(f" (took {elapsed_total} seconds)", fg="yellow"))
    else:
        spinner.fail(prefix + click.style("Scan failed", fg="red", bold=True) + click.style(f" after {elapsed_total} seconds", fg="yellow"))
        raise subprocess.CalledProcessError(process.returncode, docker_cmd)
