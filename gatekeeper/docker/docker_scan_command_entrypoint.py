import argparse
import json
import subprocess
from pathlib import Path

import yaml


def load_tools_config():
    with open("/app/tools-config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tools", required=True, help="Comma-separated tool names")
    parser.add_argument("--output", required=True, help="Findings Output file path")
    return parser.parse_args()


def main():
    args = parse_arguments()
    config = load_tools_config()

    requested_tools = set(tool.strip() for tool in args.tools.split(","))

    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    all_tools = config.get("generic_tools", []) + config.get("specific_tools", [])
    tools_to_run = [tool for tool in all_tools if tool.get("name") in requested_tools]

    results = {}
    for tool in tools_to_run:
        tool_name = tool["name"]
        tool_output = output_dir / f"{tool_name.lower()}_results.json"
        execution_command = tool["execution_command"].format(output_file=tool_output)

        try:
            subprocess.run(execution_command, shell=True, check=False, cwd="/repo")
            if tool_output.exists():
                results[tool_name] = json.loads(tool_output.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Warning: Error running {tool_name}: {e}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
