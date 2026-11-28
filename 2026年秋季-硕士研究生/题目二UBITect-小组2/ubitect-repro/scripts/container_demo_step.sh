#!/usr/bin/env bash
# Execute one DEMO step inside the persistent linux/amd64 container.
# Usage (inside container): bash /work/scripts/container_demo_step.sh ACTION CASE
set -euo pipefail
source /work/scripts/container_env.sh

CASE="${2:-}"
case "$CASE" in
    tutorial) ;;
    example)
        printf "note: 'example' is a compatibility alias for 'tutorial'; using tutorial.\n" >&2
        CASE="tutorial"
        ;;
    history) ;;
    *)
        printf 'unknown demo case: %s\n' "$CASE" >&2
        exit 2
        ;;
esac

exec "$PYTHON" -I /work/scripts/demo_step.py "$1" "$CASE"
