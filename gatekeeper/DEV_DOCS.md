# Developer Documentation

## Technologies used

- **uv** - used for dependency management/locking and developing
- **click** - Python library used to help building the CLI
- **pipx** - a tool to install and run Python applications in isolated environments with the intent of being globally available. Think of it as your "npm" or "brew" but for Python packages
- **pre-commit** - tool used for managing the pre-commit hooks that run the SAST tools on every commit

## Adding a new command

To add a new command, simply add the function that contains the command logic to the `all_cli_commands` list in `__init__.py` inside the `commands` directory

That's it, the command should now be available as a subcommand of the main CLI group. If you installed the package in editable mode, you can test it immediately by running `gatekeeper new-command` in your terminal.

## Logging and exceptions

Some utilies were created to help with printing stuff in the user's terminal. Please prefer using the utilities made available in `gatekeeper/utils/printer.py` instead of other logging solutions.

A utility exception ``CliException`` was also created to help sending uncaught exceptions to the user's terminal in a nice format, without leaking stack traces or other internal information. By using this, we can simply raise the exception wtihout worrying about catching it and reformatting the output.


It may also be helpful to apply customized styling to the messages printed to the user. For that, we can use `click.style` to apply colors and other styles to the messages. For example, we can use `click.style("Hello, World!", fg="green", bold=True)` to print "Hello, World!" in green and bold.

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