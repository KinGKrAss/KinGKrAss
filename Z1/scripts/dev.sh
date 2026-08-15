#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
Z1_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${Z1_ROOT}"
cp -n .env.example .env || true
docker compose up --build
