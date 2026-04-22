# Gatekeeper

Gatekeeper is a security tool that runs instantly and gives instant feedback by running multiple SAST tools.

It is setup as an installable package. This allows you to install it in your global Python environment and use it as a command while inside any repository to install the pre-commit hooks that it relies on to run multiple SAST tools.

You may also run the SAST tools on demand by using the CLI directly.

## Usage

### Requirements

- Python 3.13 or higher
- git
- Docker
- `pipx` (install with `pip install pipx`. *You can use `pip` if you prefer, but `pipx` is recommended*)


### Setup

1. Clone this repository and navigate to the project directory.
2. Install the gatekeeper package globally in your machine using `pipx install .` (or `pip install .`).

-  *if you are using raw pip, you have to install the dependencies first, either by using `uv sync` or `pip install -r requirements.txt`*

3. Build the Docker image for the scanning engine by running `docker build -f docker/Dockerfile -t gatekeeper-scanner .` in the project directory.

### Using Gatekeeper

- Run `gatekeeper setup` while inside any repository to set up the pre-commit hook
- Run `gatekeeper scan` to run the SAST tools on demand. This is also the command called by the pre-commit hook on every commit

## Developing

### Requirements

- uv ([install with `pipx install uv` or equivalent](https://docs.astral.sh/uv/getting-started/installation/#installation-methods))

*Optionally, you may manage the virtual environment manually and install the dependencies with any tool that you prefer*

### Setup

1. Clone the repository and navigate to the project directory.
2. Install the dependencies with `uv sync` (or your preferred method). This is important for getting autocompletion and type checking in the IDE.

- *you may use `uv sync --extra dev` for additional tooling like linters and formatters*

1. Run `pipx install . -e` to install the package in editable mode *(This allows you to make changes to the code and see the effects immediately without needing to reinstall). As mentioned previously, you can also manage the dependencies yourself and/or use raw pip*

That's it - you are now ready to develop!

Just like when using the package as a user, you also need to build the Docker image for the scanning engine to be able to test the scanning functionality. You can do this by running `docker build -f docker/Dockerfile -t gatekeeper-scanner .` in the project directory.

*You will have to repeat the step above every time you make changes to the `docker/Dockerfile`, `docker/docker_install_tools_image_step.py`, `docker/docker_scan_command_entrypoint.py`, or `tools-config.yaml`*

## Documentation

### Commands

- `gatekeeper setup` - Installs gatekeeper on the current git repository. This allows for the security checks to run on every commit
- `gatekeeper scan` - Runs the SAST tools on demand. This is also the command called by the pre-commit hook on every commit
  
  Additional arguments:
  - `--verbose` (`-v`): attaches the docker container shell to the terminal, allowing you to see the scan progress in real time

### SAST Tools

This section lists the programming languages supported by Gatekeeper and the corresponding SAST tools that are integrated into the system. Besides language-specific tools, gatekeeper also runs **Semgrep** and **Trivy** across every codebase.

- **Python** - Bandit

- **JavaScript** - ESLint (specifically with eslint-plugin-security)

- **Java** - SpotBugs (specifically with the FindSecBugs plugin)

- **Go** - gosec

- **C / C++** - Flawfinder

- **PHP** - Progpilot

### Known limitations

Pre-commit hooks have a known limitation where they can't output the stdout of the hook being run in real time.

For this reason, you will only be available to see the logs and results of the hook after it finishes running.