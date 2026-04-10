# Gatekeeper

Gatekeeper is a security tool that runs instantly, gives clear feedback, and integrates with CI/CD as a second enforcement layer.

It is setup as an installable package. This allows you to install it in your global Python environment and use it as a command while inside any repository to install the pre-commit hooks that it relies on to run multiple SAST tools.

You may also run the SAST tools on demand by using the CLI directly.

## Usage

### Requirements

- Python 3.13 or higher
- `pipx` (recommended) or raw `pip` (*install with `pip install pipx`*)
- `pre-commit` (install with `pipx install pre-commit` or `pip install pre-commit`)
- Docker

### Setup

1. Clone this repository and navigate to the project directory.
2. Install the gatekeeper package globally in your machine using `pipx install .` (or `pip install .`).

### Using Gatekeeper

- Run `gatekeeper setup` while inside any repository to set up the pre-commit hook
- Run `gatekeeper scan` to run the SAST tools on demand. This is also the command called by the pre-commit hook on every commit

## Developing

### Requirements

- uv ([install with `pip install uv` or equivalent](https://docs.astral.sh/uv/getting-started/installation/#installation-methods))

*Optionally, you may manage the virtual environment manually and install the dependencies with any tool that you prefer*

### Setup

1. Clone the repository and navigate to the project directory.
2. Install the dependencies with `uv sync` (or your preferred method).
step 3 sohuld be pipx
1. Run `uv pipx install . -e` to install the package in editable mode *(This allows you to make changes to the code and see the effects immediately without needing to reinstall)*

That's it - you are now ready to develop!

## Documentation


### Commands

- `gatekeeper setup` - Installs gatekeeper on the current git repository. This allows for the security checks to run on every commit.
- `gatekeeper scan` - Runs the SAST tools on demand. This is also the command called by the pre-commit hook on every commit.

### SAST Tools

This section lists the programming languages supported by Gatekeeper and the corresponding SAST tools that are integrated into the system. Besides language-specific tools, gatekeeper also runs **Semgrep** and **Trivy** across every codebase.

- **Python** - Bandit

- **JavaScript** - ESLint (specifically with eslint-plugin-security)

- **Java** - SpotBugs (specifically with the FindSecBugs plugin)

- **Go** - gosec

- **C / C++** - Flawfinder

- **PHP** - Progpilot

