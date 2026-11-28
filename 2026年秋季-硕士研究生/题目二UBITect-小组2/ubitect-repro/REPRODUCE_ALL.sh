#!/usr/bin/env bash
# Complete reproduction entry: generate A-D from the pinned source, then run
# the historical H1/H2 case with the freshly built tools, then verify the
# real outputs against the documented observations.
#
# Document figures/PDF generation is deliberately not part of this entry.
set -euo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
IMAGE="${UBITECT_IMAGE:-ubitect-repro-delivery:base}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ID="${UBITECT_RUN_ID:-RUN-$STAMP}"
HIST_ID="${UBITECT_HISTORY_RUN_ID:-HIST-$STAMP}"
LOG="$PROJECT/logs/reproduce-all-$RUN_ID.log"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p "$PROJECT/logs"
exec > >(tee -a "$LOG") 2>&1

section() { printf '\n=== %s ===\n' "$*"; }
fatal() { echo "FATAL: $*" >&2; exit 1; }

section "order"
echo "1. A-D : REPRODUCE.sh (run_id=$RUN_ID)"
echo "2. H1/H2: RUN_HISTORY.sh (history_run_id=$HIST_ID)"
echo "3. expected-result checks over this run's artifacts"
echo "log=$LOG"

section "A-D ($RUN_ID)"
UBITECT_RUN_ID="$RUN_ID" UBITECT_IMAGE="$IMAGE" bash "$PROJECT/REPRODUCE.sh"

section "H1/H2 ($HIST_ID)"
UBITECT_HISTORY_RUN_ID="$HIST_ID" UBITECT_IMAGE="$IMAGE" bash "$PROJECT/RUN_HISTORY.sh"

section "expected-result check"
set +e
docker run --rm --platform linux/amd64 \
    -v "$PROJECT:/work" -w /work \
    -e "UBITECT_RUN_ID=$RUN_ID" \
    -e "UBITECT_HISTORY_RUN_ID=$HIST_ID" \
    "$IMAGE" bash -lc \
    'source /work/scripts/container_env.sh; exec "$PYTHON" -I /work/scripts/check_expected.py --history-run "$UBITECT_HISTORY_RUN_ID" --run-id "$UBITECT_RUN_ID"'
RC=$?
set -e
echo "check_exit=$RC"

section "result"
FINISHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 -I "$PROJECT/scripts/record_host_env.py" \
    --out "$PROJECT/artifacts/reproduce-all-host-environment.json" \
    --image "$IMAGE" --run-id "$RUN_ID" --mode "A-D + H1/H2" \
    --started-at "$STARTED_AT" --finished-at "$FINISHED_AT" \
    --exit-code "$RC"
echo "run_id=$RUN_ID"
echo "history_run=$HIST_ID"
echo "acceptance=$PROJECT/artifacts/ACCEPTANCE.json"
echo "log=$LOG"
if [ "$RC" -ne 0 ]; then
    echo "FULL REPRODUCTION: FAIL (exit $RC)" >&2
    exit "$RC"
fi
echo "FULL REPRODUCTION: PASS (run_id=$RUN_ID history_run=$HIST_ID)"
