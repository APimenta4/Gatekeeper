# Developer Documentation

## Technologies used

- **uv** - used for dependency management/locking and developing
- **click** - used for building the CLI

## Adding a new command

To add a new command, simply add the function that contains the command logic to the `all_cli_commands` list in `__init__.py` inside the `commands` directory

That's it, the command should now be available as a subcommand of the main CLI group. If you installed the package in editable mode, you can test it immediately by running `gatekeeper new-command` in your terminal.

## Code Quality Tools

In order to enhance code quality and developer experience, some tools have been configured at the repository level in `pyproject.toml`. If something is inconsistent or if you find any issues with the configuration, feel free to change it. 

Those tools are:

- flake8
- black
- isort
- mypy

And you can run them by doing:

```bash
black src/
isort src/
flake8 src/
mypy src/
```

or by using an IDE that supports them (e.g., VSCode, PyCharm, etc. *For some IDEs, you may need to install the corresponding extensions*).