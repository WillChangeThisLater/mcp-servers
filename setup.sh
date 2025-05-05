#!/bin/bash

set -euo pipefail

# Check if a virtual environment is active and deactivate it
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    source deactivate
fi

# Check if the .venv directory exists and remove it
if [[ -d ".venv" ]]; then
    rm -rf .venv
fi

uv venv --python 3.13
source .venv/bin/activate
uv pip install .
