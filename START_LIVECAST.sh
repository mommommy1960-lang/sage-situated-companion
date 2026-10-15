#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo
echo "=== Commons Live Ensemble ==="
echo

if [ ! -x ".venv/bin/python" ]; then
  echo "Creating local Python environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

if [ ! -f ".venv/.livecast_ready" ]; then
  echo "Installing Live Ensemble dependencies. This happens once..."
  python -m pip install --upgrade pip
  python -m pip install -r apps/livecast/requirements.txt
  touch .venv/.livecast_ready
fi

python START_LIVECAST.py
