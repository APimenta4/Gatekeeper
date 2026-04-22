import subprocess

import yaml


def load_tools_config():
    with open("/app/tools-config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_tools_config()

    all_tools = config.get("generic_tools", []) + config.get("specific_tools", [])

    for tool in all_tools:
        name = tool.get("name", "unknown")
        installation_command = tool.get("installation_command")

        if not installation_command:
            print(f"Warning: No installation command for {name}, skipping.")
            continue

        print(f"Installing {name}...")
        try:
            subprocess.run(installation_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {name}: {e}")


if __name__ == "__main__":
    main()
