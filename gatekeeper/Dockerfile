FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pyyaml

WORKDIR /app

COPY tools-config.yaml /app/tools-config.yaml
COPY docker_scan_entrypoint.py /app/docker_scan_entrypoint.py

ENTRYPOINT ["python", "/app/docker_scan_entrypoint.py"]