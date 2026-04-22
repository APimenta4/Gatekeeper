FROM python:3.13-slim

# Install package managers for the tools here
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pyyaml

WORKDIR /app

COPY tools-config.yaml /app/tools-config.yaml
COPY docker/docker_install_tools_image_step.py /app/docker_install_tools_image_step.py
COPY docker/docker_scan_command_entrypoint.py /app/docker_scan_command_entrypoint.py

RUN python /app/docker_install_tools_image_step.py \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python", "/app/docker_scan_command_entrypoint.py"]