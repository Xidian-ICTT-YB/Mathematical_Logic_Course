#!/usr/bin/env bash
# Host entry point for the UBITect backlog.c A-D reproduction.
#
# The script is self-contained: it derives every path from its own directory,
# fetches the two pinned binary dependencies into ./downloads, builds the
# linux/amd64 image if needed, and runs the in-container pipeline.  It does not
# read a configuration file or tool cache outside this project.
set -euo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
IMAGE="${UBITECT_IMAGE:-ubitect-repro-delivery:base}"
DOCKER_APP="${UBITECT_DOCKER_APP:-/Applications/Docker.app}"
DOCKER_START_TIMEOUT="${UBITECT_DOCKER_START_TIMEOUT:-180}"
REBUILD_IMAGE="${UBITECT_REBUILD_IMAGE:-${REBUILD_IMAGE:-0}}"
FORCE_BUILD="${FORCE_BUILD:-0}"
STAGES="${UBITECT_STAGES:-}"

if [ -d "$DOCKER_APP/Contents/Resources/bin" ]; then
    export PATH="$DOCKER_APP/Contents/Resources/bin:$PATH"
fi

mkdir -p "$PROJECT/logs" "$PROJECT/artifacts" "$PROJECT/downloads"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ID="${UBITECT_RUN_ID:-RUN-$STAMP}"
LOG="$PROJECT/logs/reproduce-$STAMP.log"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exec > >(tee -a "$LOG") 2>&1

section() { printf '\n=== %s ===\n' "$*"; }
fatal() { echo "FATAL: $*" >&2; exit 1; }

section "host"
echo "project=$PROJECT"
echo "image=$IMAGE"
echo "run_id=$RUN_ID"
echo "log=$LOG"
uname -a
sw_vers 2>/dev/null || true
df -h "$PROJECT" | tail -n 1

command -v docker >/dev/null 2>&1 || fatal "docker CLI not found; install/start Docker Desktop"
command -v python3 >/dev/null 2>&1 || fatal "python3 is required for host-side metadata"

if ! docker info >/dev/null 2>&1; then
    if [ "$(uname -s)" = "Darwin" ] && [ -d "$DOCKER_APP" ]; then
        echo "Docker is not running; opening $DOCKER_APP"
        open -a "$DOCKER_APP" || true
        waited=0
        while ! docker info >/dev/null 2>&1; do
            [ "$waited" -ge "$DOCKER_START_TIMEOUT" ] && fatal "Docker Desktop did not become ready in ${DOCKER_START_TIMEOUT}s"
            sleep 2
            waited=$((waited + 2))
        done
    else
        fatal "Docker daemon is not available and cannot be started automatically on this platform"
    fi
fi
docker version

section "pinned downloads"
bash "$PROJECT/scripts/fetch_dependencies.sh"

section "base image"
if ! docker image inspect ubuntu:24.04 >/dev/null 2>&1; then
    if ! docker pull --platform linux/amd64 ubuntu:24.04; then
        echo "Docker Hub pull failed; trying the official Ubuntu image on public ECR" >&2
        docker pull --platform linux/amd64 public.ecr.aws/ubuntu/ubuntu:24.04
        docker tag public.ecr.aws/ubuntu/ubuntu:24.04 ubuntu:24.04
    fi
fi

section "analysis image"
if [ "$REBUILD_IMAGE" = "1" ] || ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker build --platform linux/amd64 --progress=plain \
        -t "$IMAGE" -f "$PROJECT/Dockerfile" "$PROJECT"
else
    echo "using existing $IMAGE (set UBITECT_REBUILD_IMAGE=1 to rebuild)"
fi
docker image inspect "$IMAGE" --format '{{.Id}}' | tee "$PROJECT/logs/image-id.txt"
docker image inspect "$IMAGE" --format '{{.Os}}/{{.Architecture}}' | tee "$PROJECT/logs/image-platform.txt"
test "$(cat "$PROJECT/logs/image-platform.txt")" = "linux/amd64" || \
    fatal "image $IMAGE is not linux/amd64"

section "A-D container pipeline"
set +e
docker run --rm --platform linux/amd64 \
    -v "$PROJECT:/work" -w /work \
    -e "UBITECT_RUN_ID=$RUN_ID" \
    -e "UBITECT_STAGES=$STAGES" \
    -e "FORCE_BUILD=$FORCE_BUILD" \
    "$IMAGE" bash /work/scripts/reproduce_in_container.sh
RC=$?
set -e
echo "container_exit=$RC"

section "host record"
FINISHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 -I "$PROJECT/scripts/record_host_env.py" \
    --out "$PROJECT/artifacts/host-environment.json" \
    --image "$IMAGE" --run-id "$RUN_ID" --mode "A-D" \
    --started-at "$STARTED_AT" --finished-at "$FINISHED_AT" \
    --exit-code "$RC"

section "result"
if [ -f "$PROJECT/artifacts/SUMMARY.md" ]; then
    cat "$PROJECT/artifacts/SUMMARY.md"
fi
if [ -f "$PROJECT/artifacts/VALIDATION.json" ]; then
    python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print("structure validation:", "PASS" if d.get("ok") else "FAIL")' \
        "$PROJECT/artifacts/VALIDATION.json"
fi
echo "log: $LOG"
if [ "$RC" -ne 0 ]; then
    echo "REPRODUCTION: FAIL (exit $RC)" >&2
    exit "$RC"
fi
if [ -n "$STAGES" ]; then
    echo "BUILD REPRODUCTION: PASS (run_id=$RUN_ID stages=$STAGES)"
else
    echo "A-D REPRODUCTION: PASS (run_id=$RUN_ID)"
fi
