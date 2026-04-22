import argparse
import json
import subprocess
import threading
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


def _stream_prefixed_output(tool_name, process):
    for line in process.stdout:
        text = line.decode("utf-8", errors="replace").rstrip("\n")
        print(f"[{tool_name}] {text}", flush=True)


def main():
    args = parse_arguments()
    config = load_tools_config()

    requested_tools = set(tool.strip() for tool in args.tools.split(","))

    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    all_tools = config.get("generic_tools", []) + config.get("specific_tools", [])
    tools_to_run = [tool for tool in all_tools if tool.get("name") in requested_tools]

    results = {}
    processes = {}
    output_threads = []
    for tool in tools_to_run:
        tool_name = tool["name"]
        tool_output = output_dir / f"{tool_name.lower()}_results.json"
        execution_command = tool["execution_command"].format(output_file=tool_output)

        print(f"[{tool_name}] Starting scan...", flush=True)
        process = subprocess.Popen(
            execution_command,
            shell=True,
            cwd="/repo",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        thread = threading.Thread(
            target=_stream_prefixed_output, args=(tool_name, process)
        )
        thread.start()
        output_threads.append(thread)
        processes[tool_name] = {
            "process": process,
            "output_file": tool_output,
        }

    for thread in output_threads:
        thread.join()

    for tool_name, entry in processes.items():
        entry["process"].wait()
        return_code = entry["process"].returncode
        if return_code == 0:
            print(f"[{tool_name}] Finished successfully", flush=True)
        else:
            print(f"[{tool_name}] Finished with exit code {return_code}", flush=True)
        try:
            if entry["output_file"].exists():
                results[tool_name] = json.loads(
                    entry["output_file"].read_text(encoding="utf-8")
                )
                print(f"[{tool_name}] Persisted tool results report", flush=True)
            else:
                print(f"[{tool_name}] No output file generated", flush=True)
        except Exception as e:
            print(f"[{tool_name}] Warning: Error reading results: {e}", flush=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
