#!/usr/bin/env bash
# Apple-specific startup script for MindForge
# Delegates to the cross-platform run.sh to launch the backend server

set -euo pipefail
cd "$(dirname "$0")"

# Ensure run.sh is executable and present
if [ ! -x run.sh ]; then
    chmod +x run.sh
fi

./run.sh "$@"
