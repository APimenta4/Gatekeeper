# Expose a single list containing all available CLI commands
from .scan import scan
from .setup import setup

all_cli_commands = [
    setup,
    scan,
]
