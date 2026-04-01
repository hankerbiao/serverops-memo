#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PID_FILE="${SCRIPT_DIR}/.serverops-backend.pid"
LOG_FILE="${SCRIPT_DIR}/.serverops-backend.log"
PYTHON_BIN="${PYTHON_BIN:-python3}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8889}"
RELOAD="${RELOAD:-0}"

is_running() {
  if [[ ! -f "${PID_FILE}" ]]; then
    return 1
  fi

  local pid
  pid="$(cat "${PID_FILE}")"
  if [[ -z "${pid}" ]]; then
    return 1
  fi

  if kill -0 "${pid}" 2>/dev/null; then
    return 0
  fi

  rm -f "${PID_FILE}"
  return 1
}

start_server() {
  if is_running; then
    echo "Backend already running with PID $(cat "${PID_FILE}")"
    return 0
  fi

  cd "${REPO_ROOT}"
  local -a cmd=("${PYTHON_BIN}" -m uvicorn backend.main:app --host "${HOST}" --port "${PORT}")
  if [[ "${RELOAD}" == "1" ]]; then
    cmd+=(--reload)
  fi

  nohup "${cmd[@]}" >"${LOG_FILE}" 2>&1 &
  echo $! > "${PID_FILE}"
  sleep 1

  if is_running; then
    echo "Backend started on http://${HOST}:${PORT} (PID $(cat "${PID_FILE}"))"
    echo "Log file: ${LOG_FILE}"
    if [[ "${RELOAD}" == "1" ]]; then
      echo "Reload mode: enabled"
    fi
    return 0
  fi

  echo "Failed to start backend. Check ${LOG_FILE}" >&2
  rm -f "${PID_FILE}"
  return 1
}

stop_server() {
  if ! is_running; then
    echo "Backend is not running"
    return 0
  fi

  local pid
  pid="$(cat "${PID_FILE}")"
  kill "${pid}"

  for _ in {1..10}; do
    if ! kill -0 "${pid}" 2>/dev/null; then
      rm -f "${PID_FILE}"
      echo "Backend stopped"
      return 0
    fi
    sleep 1
  done

  echo "Backend did not stop gracefully; sending SIGKILL"
  kill -9 "${pid}" 2>/dev/null || true
  rm -f "${PID_FILE}"
  echo "Backend stopped"
}

show_status() {
  if is_running; then
    echo "Backend is running with PID $(cat "${PID_FILE}") on http://${HOST}:${PORT}"
  else
    echo "Backend is not running"
  fi
}

show_logs() {
  if [[ -f "${LOG_FILE}" ]]; then
    tail -n 50 "${LOG_FILE}"
  else
    echo "No log file found at ${LOG_FILE}"
  fi
}

case "${1:-}" in
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  restart)
    stop_server
    start_server
    ;;
  status)
    show_status
    ;;
  logs)
    show_logs
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs}" >&2
    exit 1
    ;;
esac
