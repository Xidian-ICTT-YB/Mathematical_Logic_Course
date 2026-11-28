#!/usr/bin/env bash
# Host entry point for the historical ahci_xgene H1/H2 case.
#
# Prerequisites: the linux/amd64 image and the in-container toolchain.  If the
# toolchain is missing this script builds it through REPRODUCE.sh with only the
# build stages enabled; it never regenerates or deletes the A-D artifacts.
set -euo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
IMAGE="${UBITECT_IMAGE:-ubitect-repro-delivery:base}"
DOCKER_APP="${UBITECT_DOCKER_APP:-/Applications/Docker.app}"
DOCKER_START_TIMEOUT="${UBITECT_DOCKER_START_TIMEOUT:-180}"

if [ -d "$DOCKER_APP/Contents/Resources/bin" ]; then
    export PATH="$DOCKER_APP/Contents/Resources/bin:$PATH"
fi

mkdir -p "$PROJECT/logs" "$PROJECT/history/ahci_xgene/runs"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ID="${UBITECT_HISTORY_RUN_ID:-HIST-$STAMP}"
LOG="$PROJECT/logs/run-history-$STAMP.log"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exec > >(tee -a "$LOG") 2>&1

section() { printf '\n=== %s ===\n' "$*"; }
fatal() { echo "FATAL: $*" >&2; exit 1; }

section "host"
echo "project=$PROJECT"
echo "image=$IMAGE"
echo "history_run_id=$RUN_ID"
echo "log=$LOG"
uname -a
sw_vers 2>/dev/null || true

command -v docker >/dev/null 2>&1 || fatal "docker CLI not found"
if ! docker info >/dev/null 2>&1; then
    if [ "$(uname -s)" = "Darwin" ] && [ -d "$DOCKER_APP" ]; then
        open -a "$DOCKER_APP" || true
        waited=0
        while ! docker info >/dev/null 2>&1; do
            [ "$waited" -ge "$DOCKER_START_TIMEOUT" ] && fatal "Docker Desktop did not become ready in ${DOCKER_START_TIMEOUT}s"
            sleep 2
            waited=$((waited + 2))
        done
    else
        fatal "Docker daemon is not available"
    fi
fi

section "toolchain"
TOOLS_OK=1
for f in build/bbtag/bbTaglib.so build/ubitect-original/ubitect \
         build/klee-original/bin/klee build/klee-original/bin/klee.noexport \
         .venv-linux/bin/python; do
    # The venv interpreter is a symlink into the container path; on the host it
    # is necessarily dangling, so accept a symlink as a present toolchain.
    if [ ! -e "$PROJECT/$f" ] && [ ! -L "$PROJECT/$f" ]; then
        TOOLS_OK=0
    fi
done
if [ "$TOOLS_OK" = "0" ]; then
    echo "toolchain incomplete; building bootstrap/prepare-source/build-all only"
    UBITECT_STAGES="bootstrap prepare-source build-all" \
    UBITECT_RUN_ID="BUILD-$STAMP" \
    UBITECT_IMAGE="$IMAGE" \
        bash "$PROJECT/REPRODUCE.sh"
else
    echo "toolchain present; reusing $PROJECT/build"
fi
test -e "$PROJECT/history/ahci_xgene/runs/$RUN_ID" && \
    fatal "history run already exists: history/ahci_xgene/runs/$RUN_ID"

section "H1/H2 container run"
set +e
docker run --rm --platform linux/amd64 \
    -v "$PROJECT:/work" -w /work \
    -e "UBITECT_HISTORY_RUN_ID=$RUN_ID" \
    "$IMAGE" bash -lc \
    'source /work/scripts/container_env.sh; exec "$PYTHON" -I /work/scripts/run_history_case.py --run-id "$UBITECT_HISTORY_RUN_ID"'
RC=$?
set -e
echo "container_exit=$RC"

section "host record"
FINISHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 -I "$PROJECT/scripts/record_host_env.py" \
    --out "$PROJECT/history/ahci_xgene/runs/$RUN_ID/host-environment.json" \
    --image "$IMAGE" --run-id "$RUN_ID" --mode "H1/H2" \
    --started-at "$STARTED_AT" --finished-at "$FINISHED_AT" \
    --exit-code "$RC"

if [ -f "$PROJECT/history/ahci_xgene/runs/$RUN_ID/summary.json" ]; then
    printf '%s\n' "$RUN_ID" > "$PROJECT/history/ahci_xgene/runs/LAST_RUN.txt"
fi

section "result"
if [ -f "$PROJECT/history/ahci_xgene/runs/$RUN_ID/summary.json" ]; then
    python3 -I - "$PROJECT/history/ahci_xgene/runs/$RUN_ID/summary.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
for h in d.get("histories", []):
    print(f"{h['version']}: candidates={h['candidate_count']} "
          f"target_objects={h['target_warning_count']} "
          f"confirmed_objects={h['target_confirmed_count']} "
          f"use_points={h['target_confirmed_lines']}")
print("H1 target confirmed:", d.get("target_h1_confirmed"))
print("H2 target confirmed:", d.get("target_h2_confirmed"))
PY
fi
echo "history_run=$RUN_ID"
echo "run_dir=$PROJECT/history/ahci_xgene/runs/$RUN_ID"
echo "log=$LOG"
if [ "$RC" -ne 0 ]; then
    echo "H1/H2 REPRODUCTION: FAIL (exit $RC)" >&2
    exit "$RC"
fi
echo "H1/H2 REPRODUCTION: PASS (run_id=$RUN_ID)"
