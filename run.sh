#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=".env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: '$ENV_FILE' not found. Please copy 'sample.env' and populate it with required variables. "
  exit 1
fi

echo "Found '$ENV_FILE'. Starting services with docker-compose..."
docker-compose up --build
