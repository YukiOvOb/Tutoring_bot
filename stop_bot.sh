#!/usr/bin/env bash
set -euo pipefail

# Stop telegram_bot.py processes gracefully, fall back to SIGKILL after timeout
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[stop_bot] Working directory: $SCRIPT_DIR"

# Find PIDs matching the script name
pids=$(pgrep -f "telegram_bot.py" || true)
if [ -z "$pids" ]; then
  echo "[stop_bot] No running telegram_bot.py processes found."
  exit 0
fi

echo "[stop_bot] Found PIDs: $pids"

# Try graceful termination
kill $pids || true

# Wait up to 5 seconds
for i in {1..5}; do
  sleep 1
  remaining=$(pgrep -f "telegram_bot.py" || true)
  if [ -z "$remaining" ]; then
    echo "[stop_bot] Processes terminated gracefully."
    break
  fi
  echo "[stop_bot] Waiting for processes to exit... ($i)"
done

# If still running, force kill
remaining=$(pgrep -f "telegram_bot.py" || true)
if [ -n "$remaining" ]; then
  echo "[stop_bot] Forcing kill for: $remaining"
  kill -9 $remaining || true
fi

# Remove PID file if present
if [ -f "$SCRIPT_DIR/bot.pid" ]; then
  rm -f "$SCRIPT_DIR/bot.pid" && echo "[stop_bot] Removed bot.pid"
fi

echo "[stop_bot] Done."
