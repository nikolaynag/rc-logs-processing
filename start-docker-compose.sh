#!/bin/bash
set -eu
SCRIPT_FILE="$(readlink -f "$0")"
export WORKDIR="$(dirname "$SCRIPT_FILE")"
cd "$WORKDIR"
docker-compose up
