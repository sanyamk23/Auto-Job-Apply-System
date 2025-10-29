#!/usr/bin/env bash
# Helper to run this project from Git Bash on Windows
# - activates the venv
# - sets PYTHONPATH to the project root and src
# - runs the main application

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

# Activate virtualenv (Windows venv layout)
if [ -f "${PROJECT_ROOT}/venv/Scripts/activate" ]; then
  # Git Bash: use the Windows virtualenv activation script
  source "${PROJECT_ROOT}/venv/Scripts/activate"
else
  echo "Warning: venv activation script not found at ${PROJECT_ROOT}/venv/Scripts/activate"
fi

# Export PYTHONPATH for this session so imports like 'config.api_config' resolve
export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_ROOT}/src:${PYTHONPATH:-}"

# Run main
python "${PROJECT_ROOT}/src/main.py" "$@"
