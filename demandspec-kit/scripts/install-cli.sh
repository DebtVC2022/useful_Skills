#!/usr/bin/env bash
set -euo pipefail
KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python -m pip install -e "$KIT_ROOT"
echo "DemandSpec CLI installed. Run: demandspec --version"
