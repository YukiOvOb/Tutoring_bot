#!/usr/bin/env bash
set -euo pipefail

# Pull latest code from git, install deps (if requirements.txt exists) and run telegram_bot.py in background
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[pull_and_run] Working directory: $SCRIPT_DIR"

# Stop existing bot first
if [ -x "$SCRIPT_DIR/stop_bot.sh" ]; then
  echo "[pull_and_run] Stopping existing bot..."
  "$SCRIPT_DIR/stop_bot.sh"
else
  echo "[pull_and_run] stop_bot.sh not executable or missing; attempting to stop by pgrep"
  pids=$(pgrep -f "telegram_bot.py" || true)
  if [ -n "$pids" ]; then
    kill $pids || true
    sleep 1
  fi
fi

# Update code from git if repository present
if [ -d .git ]; then
  echo "[pull_and_run] Fetching latest from origin..."
  git fetch --all --prune
  echo "[pull_and_run] Pulling..."
  git pull --ff-only || git pull || true
else
  echo "[pull_and_run] No .git directory found; skipping git pull."
fi

# Activate virtualenv if present
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
  echo "[pull_and_run] Activating virtualenv .venv"
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.venv/bin/activate"
  PIP_CMD="pip"
else
  echo "[pull_and_run] No .venv found, using system pip3"
  PIP_CMD="pip3"
fi

# Install requirements if present
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
  echo "[pull_and_run] Installing requirements..."
  $PIP_CMD install -r requirements.txt
else
  echo "[pull_and_run] No requirements.txt found; skipping pip install."
fi

# Start bot in background using nohup, write PID to bot.pid
LOGFILE="$SCRIPT_DIR/bot.log"
PIDFILE="$SCRIPT_DIR/bot.pid"

echo "[pull_and_run] Starting telegram_bot.py (logs -> $LOGFILE)"
nohup python3 "$SCRIPT_DIR/telegram_bot.py" >> "$LOGFILE" 2>&1 &
bot_pid=$!

echo $bot_pid > "$PIDFILE"

echo "[pull_and_run] Bot started with PID $bot_pid"

echo "[pull_and_run] Done. Check $LOGFILE for runtime logs."
