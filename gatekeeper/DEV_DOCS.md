# Developer Documentation

## Technologies used

- **uv** - used for dependency management/locking and developing
- **click** - used for building the CLI

## Adding a new command

1. Create a new file in the `commands` directory with the name of the command you want to add (e.g., `new_command.py`)
2. In this file, define a *public* function that implements the logic for your command. You may also create private helper functions *(starting with "_", e.g., `_helper_function`)*
3. Reexport the function in `__init__.py` in the `commands` directory

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