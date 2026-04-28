from pathlib import Path

# maybe make this a configuration file and use "OS.GETENV instead"
SCAN_ENGINE_FINDINGS_FILE_NAME = "findings.json"
TOOLS_CONFIG_PATH = Path(__file__).parent / "tools-config.yaml"
