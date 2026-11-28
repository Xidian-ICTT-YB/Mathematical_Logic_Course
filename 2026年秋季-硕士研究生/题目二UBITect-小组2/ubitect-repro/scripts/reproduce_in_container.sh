#!/usr/bin/env bash
# Full in-container A-D pipeline.  Invoked by the host REPRODUCE.sh.
# Every stage is logged and its real exit code is recorded before the next
# stage starts; a failure stops the pipeline at the first failing stage.
#
# UBITECT_STAGES may restrict the run to a space-separated subset of the five
# stages (used by RUN_HISTORY.sh to build the toolchain without overwriting the
# A-D evidence).  The default is the full A-D pipeline.
set -euo pipefail

ROOT="${ROOT:-/work}"
RUN_ID="${UBITECT_RUN_ID:-RUN-$(date -u +%Y%m%dT%H%M%SZ)}"
ALL_STAGES="bootstrap prepare-source build-all run-experiments validate-artifacts"
REQUESTED="${UBITECT_STAGES:-$ALL_STAGES}"
cd "$ROOT"
test "$(uname -m)" = "x86_64" || {
    echo "FATAL: container is not linux/amd64 (uname -m=$(uname -m))" >&2
    exit 90
}

mkdir -p "$ROOT/logs" "$ROOT/artifacts"
: > "$ROOT/logs/stage-exit-codes.txt"
: > "$ROOT/logs/stage-timings.tsv"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

should_run() {
    case " $REQUESTED " in
        *" $1 "*) return 0 ;;
        *) return 1 ;;
    esac
}

run_stage() {
    local name="$1"; shift
    local started ended rc duration
    started="$(date +%s.%N)"
    printf '\n=== %s ===\n' "$name"
    set +e
    "$@" 2>&1 | tee "$ROOT/logs/$name.log"
    rc=${PIPESTATUS[0]}
    set -e
    ended="$(date +%s.%N)"
    duration="$(awk -v a="$started" -v b="$ended" 'BEGIN { printf "%.3f", b - a }')"
    printf '%s rc=%s duration_s=%s\n' "$name" "$rc" "$duration" \
        | tee -a "$ROOT/logs/stage-exit-codes.txt"
    printf '%s\t%s\t%s\n' "$name" "$rc" "$duration" \
        >> "$ROOT/logs/stage-timings.tsv"
    return "$rc"
}

echo "run_id=$RUN_ID"
echo "started_utc=$STARTED_AT"
echo "container=$(uname -srm)"
echo "workdir=$ROOT"
echo "stages=$REQUESTED"

if should_run bootstrap; then
    run_stage bootstrap bash "$ROOT/scripts/container_bootstrap.sh"
fi
if should_run prepare-source; then
    run_stage prepare-source bash "$ROOT/scripts/prepare_source.sh"
fi
# container_env.sh defines PYTHON/VENV/Z3_* for the remaining stages.
source "$ROOT/scripts/container_env.sh"
if should_run build-all; then
    run_stage build-all bash "$ROOT/scripts/build_all.sh"
fi
if should_run run-experiments; then
    run_stage run-experiments "$PYTHON" -I "$ROOT/scripts/run_experiments.py"
fi
if should_run validate-artifacts; then
    run_stage validate-artifacts "$PYTHON" -I "$ROOT/scripts/validate_artifacts.py"
fi

FINISHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ "$REQUESTED" = "$ALL_STAGES" ]; then
    META_OUT="$ROOT/artifacts/RUN_METADATA.json"
    echo "A-D PIPELINE: PASS (run_id=$RUN_ID)"
else
    META_OUT="$ROOT/artifacts/BUILD_METADATA.json"
    echo "BUILD PIPELINE: PASS (run_id=$RUN_ID, stages=$REQUESTED)"
fi
"$PYTHON" -I "$ROOT/scripts/write_run_metadata.py" \
    --run-id "$RUN_ID" --started-at "$STARTED_AT" --finished-at "$FINISHED_AT" \
    --stage-file "$ROOT/logs/stage-exit-codes.txt" \
    --timing-file "$ROOT/logs/stage-timings.tsv" \
    --out "$META_OUT"
