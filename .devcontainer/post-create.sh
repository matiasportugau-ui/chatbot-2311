#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] Starting post-create setup..."

# Python dependencies
pip install --upgrade pip
if [[ -f requirements.txt ]]; then
    echo "[devcontainer] Installing Python deps..."
    pip install -r requirements.txt
else
    echo "[devcontainer] requirements.txt not found, skipping Python deps"
fi

# Node dependencies for the Next.js app
if [[ -d nextjs-app ]]; then
    pushd nextjs-app >/dev/null
    if [[ -f package-lock.json ]]; then
        echo "[devcontainer] Installing Node deps with npm ci..."
        npm ci
    elif [[ -f package.json ]]; then
        echo "[devcontainer] Installing Node deps with npm install..."
        npm install
    else
        echo "[devcontainer] package.json not found, skipping Node deps"
    fi
    popd >/dev/null
else
    echo "[devcontainer] nextjs-app directory not found, skipping Node deps"
fi

echo "[devcontainer] Post-create setup completed."
