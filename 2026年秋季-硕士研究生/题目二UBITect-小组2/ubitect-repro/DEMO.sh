#!/usr/bin/env bash
# Stepwise live demo entry.
#
# The demo runs in ONE persistent project-managed linux/amd64 container.  The
# container is created by `start`, reused by every step through `docker exec`,
# inspected by `status`, and only stopped (never removed) by `stop`.
#
# Every compile/candidates/verify/... step performs a real command in a fresh
# DEMO-* run directory; no old result is substituted.  The image and toolchain
# are reused exactly as built; nothing here rebuilds Docker/LLVM/KLEE.
set -euo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
IMAGE="${UBITECT_IMAGE:-ubitect-repro-delivery:base}"
CONTAINER="${UBITECT_CONTAINER:-ubitect-repro-delivery-demo}"
PROJECT_LABEL_KEY="com.ubitect.repro.project"
PROJECT_LABEL_VALUE="ubitect-repro-delivery"
MANAGED_LABEL_KEY="com.ubitect.repro.managed"
DOCKER_APP="${UBITECT_DOCKER_APP:-/Applications/Docker.app}"
DOCKER_START_TIMEOUT="${UBITECT_DOCKER_START_TIMEOUT:-120}"
DOCKER_POLL_SECONDS="${UBITECT_DOCKER_POLL_SECONDS:-2}"

if [ -d "$DOCKER_APP/Contents/Resources/bin" ]; then
    export PATH="$DOCKER_APP/Contents/Resources/bin:$PATH"
fi
HOST_PY="${UBITECT_HOST_PYTHON:-$(command -v python3)}"
LOGDIR="$PROJECT/logs/demo-live"
mkdir -p "$PROJECT/demo/runs" "$PROJECT/logs" "$LOGDIR"

say()  { printf '%s\n' "$*"; }
fail() { printf 'DEMO FAILED: %s\n' "$*" >&2; exit 1; }
show_exec() {
    printf '  exec:'
    printf ' %q' "$@"
    printf '\n'
}

usage() {
    cat >&2 <<'EOF'
usage: ./DEMO.sh start|status|stop
       ./DEMO.sh check|resources|summary
       ./DEMO.sh source|compile|candidates|verify|constraints|compare tutorial
       ./DEMO.sh source|compile|candidates|verify|constraints|compare history

tutorial is the formal demo case name.  `example` is accepted as a
compatibility alias and resolves to the same tutorial run and state.

The experiment container is persistent:
  start   start Docker Desktop if needed, verify the image, create/reuse the
          project container, and show the in-container system check
  status  read the real Docker/container state (nothing is started)
  stop    stop only the project container; Docker Desktop and demo results stay
EOF
}

docker_ok() { docker info >/dev/null 2>&1; }

docker_server() {
    docker version --format '{{.Server.Version}} {{.Server.Arch}}' 2>/dev/null || true
}

image_id() {
    docker image inspect "$IMAGE" --format '{{.Id}}' 2>/dev/null || true
}

image_platform() {
    docker image inspect "$IMAGE" --format '{{.Os}}/{{.Architecture}}' 2>/dev/null || true
}

container_exists() { docker inspect "$CONTAINER" >/dev/null 2>&1; }
container_running() {
    [ "$(docker inspect "$CONTAINER" --format '{{.State.Running}}' 2>/dev/null || echo false)" = "true" ]
}
container_running_text() {
    if container_running; then printf 'true'; else printf 'false'; fi
}
container_id() { docker inspect "$CONTAINER" --format '{{.Id}}' 2>/dev/null || true; }
container_label() {
    docker inspect "$CONTAINER" --format "{{index .Config.Labels \"$PROJECT_LABEL_KEY\"}}" 2>/dev/null || true
}
container_managed() {
    docker inspect "$CONTAINER" --format "{{index .Config.Labels \"$MANAGED_LABEL_KEY\"}}" 2>/dev/null || true
}
container_mount_source() {
    docker inspect "$CONTAINER" --format \
        '{{range .Mounts}}{{if eq .Destination "/work"}}{{.Source}}{{end}}{{end}}' 2>/dev/null || true
}
container_workdir() {
    docker inspect "$CONTAINER" --format '{{.Config.WorkingDir}}' 2>/dev/null || true
}
container_image_ref() {
    docker inspect "$CONTAINER" --format '{{.Config.Image}}' 2>/dev/null || true
}
container_image_id() {
    docker inspect "$CONTAINER" --format '{{.Image}}' 2>/dev/null || true
}
container_state_text() {
    docker inspect "$CONTAINER" --format '{{.State.Status}}' 2>/dev/null || true
}

owned_container() {
    [ "$(container_label)" = "$PROJECT_LABEL_VALUE" ] \
        && [ "$(container_managed)" = "true" ]
}

container_valid() {
    container_exists || return 1
    owned_container || return 1
    [ "$(container_image_id)" = "$(image_id)" ] || return 1
    [ "$(container_workdir)" = "/work" ] || return 1
    [ "$(container_mount_source)" = "$PROJECT" ] || return 1
    [ "$(image_platform)" = "linux/amd64" ] || return 1
    return 0
}

ensure_docker() {
    say "[docker]"
    say "  host: $(uname -s) $(uname -m) $(sw_vers -productVersion 2>/dev/null || true)"
    if docker_ok; then
        say "  Docker Desktop: already running (server $(docker_server))"
        return 0
    fi
    say "  Docker Desktop: not running"
    [ "$(uname -s)" = "Darwin" ] || fail "Docker is not running and automatic start is only implemented for macOS"
    [ -d "$DOCKER_APP" ] || fail "Docker Desktop app not found at $DOCKER_APP"
    say "  start command: open -a $DOCKER_APP"
    open -a "$DOCKER_APP" || fail "failed to launch Docker Desktop"
    local waited=0
    while ! docker_ok; do
        if [ "$waited" -ge "$DOCKER_START_TIMEOUT" ]; then
            fail "Docker Desktop did not become ready within ${DOCKER_START_TIMEOUT}s; check Docker Desktop and rerun ./DEMO.sh start"
        fi
        sleep "$DOCKER_POLL_SECONDS"
        waited=$((waited + DOCKER_POLL_SECONDS))
        say "  waiting for Docker Desktop ... ${waited}s"
    done
    say "  Docker Desktop: ready after ${waited}s (server $(docker_server))"
}

ensure_image() {
    say "[image]"
    if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
        fail "image $IMAGE is missing; run ./REPRODUCE_ALL.sh (or ./REPRODUCE.sh) once. This demo never downloads or rebuilds the image automatically."
    fi
    say "  image: $IMAGE"
    say "  image_id: $(image_id)"
    say "  platform: $(image_platform)"
}

write_container_record() {
    local started_by="$1"
    UBITECT_CONTAINER="$CONTAINER" UBITECT_PROJECT="$PROJECT" \
    UBITECT_CONTAINER_ID="$(container_id)" UBITECT_IMAGE="$IMAGE" \
    UBITECT_IMAGE_ID="$(image_id)" UBITECT_PLATFORM="$(image_platform)" \
    UBITECT_STARTED_BY="$started_by" \
    "$HOST_PY" -I - <<'PY'
import datetime as dt
import json
import os
import pathlib
root = pathlib.Path(os.environ["UBITECT_PROJECT"])
out = root / "demo/container.json"
out.parent.mkdir(parents=True, exist_ok=True)
try:
    previous = json.loads(out.read_text(encoding="utf-8"))
except Exception:
    previous = {}
created_by = previous.get("created_by") or previous.get("started_by")
if previous.get("id") != os.environ["UBITECT_CONTAINER_ID"] or not created_by:
    created_by = os.environ["UBITECT_STARTED_BY"]
payload = {
    "name": os.environ["UBITECT_CONTAINER"],
    "id": os.environ["UBITECT_CONTAINER_ID"],
    "image": os.environ["UBITECT_IMAGE"],
    "image_id": os.environ["UBITECT_IMAGE_ID"],
    "platform": os.environ["UBITECT_PLATFORM"],
    "workdir": "/work",
    "mount": {"source": str(root), "destination": "/work"},
    "label": {"com.ubitect.repro.project": "ubitect-repro",
              "com.ubitect.repro.managed": "true"},
    "created_by": created_by,
    "last_action": os.environ["UBITECT_STARTED_BY"],
    "recorded_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
}
out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"  record: {out.relative_to(root)}")
PY
}

show_container() {
    say "[container]"
    say "  name: $CONTAINER"
    say "  container_id: $(container_id)"
    say "  image: $(container_image_ref) ($(container_image_id))"
    say "  platform: $(image_platform)"
    say "  state: $(container_state_text)"
    say "  workdir: $(container_workdir)"
    say "  mount: $(container_mount_source) -> /work"
    say "  label: $PROJECT_LABEL_KEY=$(container_label) $MANAGED_LABEL_KEY=$(container_managed)"
}

container_system_check() {
    say "[container check]"
    show_exec docker exec -w /work "$CONTAINER" bash /work/scripts/container_system_check.sh
    docker exec -w /work "$CONTAINER" bash /work/scripts/container_system_check.sh
}

wait_running() {
    local waited=0
    while ! container_running; do
        if [ "$waited" -ge 10 ]; then
            fail "container $CONTAINER did not reach running state"
        fi
        sleep 1
        waited=$((waited + 1))
    done
}

start_demo() {
    ensure_docker
    ensure_image

    if container_exists; then
        if ! owned_container; then
            fail "container name $CONTAINER exists but is not owned by this project ($PROJECT_LABEL_KEY=$(container_label)); refusing to touch it"
        fi
        if container_valid; then
            if container_running; then
                say "[container]"
                say "  already running: reusing $CONTAINER"
                show_container
                write_container_record "already running"
                container_system_check
                return 0
            fi
            say "[container]"
            say "  start command: docker start $CONTAINER"
            docker start "$CONTAINER" >/dev/null
            say "  docker start rc: 0"
            wait_running
            show_container
            write_container_record "docker start"
            container_system_check
            return 0
        fi
        say "[container]"
        say "  existing project container does not match image/mount/platform/workdir; recreating"
        say "  stop command: docker stop $CONTAINER"
        docker stop "$CONTAINER" >/dev/null 2>&1 || true
        say "  remove command: docker rm $CONTAINER"
        docker rm "$CONTAINER" >/dev/null 2>&1 || true
    fi

    local run_cmd=(docker run -d --name "$CONTAINER" --platform linux/amd64
        --label "$PROJECT_LABEL_KEY=$PROJECT_LABEL_VALUE"
        --label "$MANAGED_LABEL_KEY=true"
        -v "$PROJECT:/work" -w /work "$IMAGE" sleep infinity)
    say "[container]"
    printf '  run command:'
    printf ' %q' "${run_cmd[@]}"
    printf '\n'
    "${run_cmd[@]}" >/dev/null
    wait_running
    show_container
    write_container_record "docker run"
    container_system_check
}

status_demo() {
    say "[docker]"
    say "  host: $(uname -s) $(uname -m) $(sw_vers -productVersion 2>/dev/null || true)"
    if ! docker_ok; then
        say "  Docker Desktop: not running"
        say "  container: unavailable (Docker not running)"
        return 0
    fi
    say "  Docker Desktop: running (server $(docker_server))"
    say "[container]"
    if ! container_exists; then
        say "  name: $CONTAINER"
        say "  state: not created"
        say "  image: $IMAGE ($(image_id))"
        say "  platform: $(image_platform)"
        say "  container_running: false"
    else
        say "  name: $CONTAINER"
        say "  container_id: $(container_id)"
        say "  state: $(container_state_text)"
        say "  container_running: $(container_running_text)"
        say "  image: $(container_image_ref) ($(container_image_id))"
        say "  platform: $(image_platform)"
        say "  workdir: $(container_workdir)"
        say "  mount: $(container_mount_source) -> /work"
        say "  label: $PROJECT_LABEL_KEY=$(container_label) $MANAGED_LABEL_KEY=$(container_managed)"
    fi
    say "[state]"
    UBITECT_PROJECT="$PROJECT" "$HOST_PY" -I - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ["UBITECT_PROJECT"])
p = root / "demo/state.json"
try:
    s = json.loads(p.read_text(encoding="utf-8"))
except Exception:
    s = {}
tutorial = s.get("tutorial_run")
print(f"  tutorial_run: {tutorial or 'none'}")
for key in ("tutorial_step", "history_run", "history_step"):
    if s.get(key):
        print(f"  {key}: {s[key]}")
m = s.get("naming_migration") or {}
if m:
    print(f"  naming_migration: v{m.get('version')} from {m.get('chosen_from')}"
          f" -> {m.get('chosen_run')} (backup {m.get('backup')})")
PY
    return 0
}

stop_demo() {
    say "[docker]"
    if ! docker_ok; then
        say "  Docker Desktop: not running"
        say "  container: not running (nothing to stop)"
        return 0
    fi
    say "  Docker Desktop: running"
    say "[container]"
    if ! container_exists; then
        say "  name: $CONTAINER"
        say "  state: not created (nothing to stop)"
        return 0
    fi
    if ! owned_container; then
        fail "container name $CONTAINER exists but is not owned by this project; refusing to stop it"
    fi
    say "  name: $CONTAINER"
    say "  container_id: $(container_id)"
    if ! container_running; then
        say "  state: already stopped"
    else
        say "  stop command: docker stop $CONTAINER"
        docker stop "$CONTAINER" >/dev/null
        say "  docker stop rc: 0"
        say "  state: $(container_state_text)"
    fi
    say "  preserved: demo/state.json, demo/runs/, artifacts/, history/, metrics/"
    say "  Docker Desktop is left running; only the project container was stopped."
}

ensure_runtime() {
    if docker_ok && container_running && container_valid; then
        say "[container]"
        say "  reusing running container: $CONTAINER"
        say "  container_id: $(container_id)"
        return 0
    fi
    start_demo
}

artifact_hint() {
    local action="$1" case_name="$2" run_dir="$3"
    case "$case_name:$action" in
        tutorial:source)   say "  artifacts: $run_dir/source/backlog.c" ;;
        tutorial:compile)  say "  artifacts: $run_dir/A/backlog.bc $run_dir/A/backlog.bb.ll $run_dir/A/compile.log $run_dir/A/bbtag.log" ;;
        tutorial:candidates) say "  artifacts: $run_dir/A/warnings.json $run_dir/A/stage1.log" ;;
        tutorial:verify)   say "  artifacts: $run_dir/A/candidate-01/verify.json $run_dir/A/candidate-01/klee-smt-export/query.smt2 $run_dir/A/candidate-01/klee-smt-export/command.txt" ;;
        tutorial:constraints) say "  artifacts: $run_dir/A/candidate-01/klee-smt-export/z3-replay.json $run_dir/A/candidate-01/klee-smt-export/z3-replay.log" ;;
        tutorial:compare)  say "  artifacts: $run_dir/compare.json $run_dir/variants/*/stage1.log" ;;
        history:source)   say "  artifacts: $run_dir/source/ $run_dir/provenance/official-fix.patch $run_dir/HARNESS_MAPPING.md $run_dir/KLEE_BRIDGE.md" ;;
        history:compile)  say "  artifacts: $run_dir/h1/ahci_xgene_h1.bc $run_dir/h2/ahci_xgene_h2.bc $run_dir/h1/compile.log $run_dir/h2/compile.log" ;;
        history:candidates) say "  artifacts: $run_dir/h1/warnings.json $run_dir/h2/warnings.json $run_dir/h1/stage1.log $run_dir/h2/stage1.log" ;;
        history:verify)   say "  artifacts: $run_dir/verify.json $run_dir/h1/confirm_result.json $run_dir/h2/confirm_result.absent.txt" ;;
        history:constraints) say "  artifacts: $run_dir/h1/candidates/candidate-*/klee-smt-export/z3-replay.json $run_dir/verify.json" ;;
        history:compare)  say "  artifacts: $run_dir/compare.json $run_dir/verify.json" ;;
    esac
}

current_run_dir() {
    local case_name="$1"
    UBITECT_PROJECT="$PROJECT" UBITECT_CASE="$case_name" "$HOST_PY" -I - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ["UBITECT_PROJECT"])
case = os.environ["UBITECT_CASE"]
try:
    s = json.loads((root / "demo/state.json").read_text(encoding="utf-8"))
except Exception:
    s = {}
if case not in ("tutorial", "history"):
    raise SystemExit(f"unknown demo case: {case}")
value = s.get(f"{case}_run")
print(root / "demo/runs" / value if value else "")
PY
}

ensure_state_migration() {
    [ -f "$PROJECT/demo/state.json" ] || return 0
    UBITECT_PROJECT="$PROJECT" "$HOST_PY" -I \
        "$PROJECT/scripts/demo_state_migration.py" "$PROJECT"
}

stage_exec() {
    local action="$1" case_name="$2" run_dir log rc
    ensure_runtime
    run_dir="$(current_run_dir "$case_name")"
    log="$LOGDIR/$(date -u +%Y%m%dT%H%M%SZ)-${action}-${case_name}.log"

    say "[stage] $action $case_name"
    say "  container: $CONTAINER"
    say "  container_id: $(container_id)"
    say "  workdir: /work"
    show_exec docker exec -w /work "$CONTAINER" bash /work/scripts/container_demo_step.sh "$action" "$case_name"
    say "  log: ${log#$PROJECT/}"
    if docker exec -w /work "$CONTAINER" bash /work/scripts/container_demo_step.sh "$action" "$case_name" 2>&1 | tee "$log"; then
        rc=0
    else
        rc=$?
    fi
    say "  rc: $rc"
    run_dir="$(current_run_dir "$case_name")"
    if [ -n "$run_dir" ]; then
        say "  run_dir: ${run_dir#$PROJECT/}"
        artifact_hint "$action" "$case_name" "${run_dir#$PROJECT/}"
    fi
    return "$rc"
}

if [ "$#" -lt 1 ]; then
    usage
    exit 2
fi

ACTION="$1"
ensure_state_migration
case "$ACTION" in
    start)
        [ "$#" -eq 1 ] || { usage; exit 2; }
        start_demo
        exit 0
        ;;
    status)
        [ "$#" -eq 1 ] || { usage; exit 2; }
        status_demo
        exit 0
        ;;
    stop)
        [ "$#" -eq 1 ] || { usage; exit 2; }
        stop_demo
        exit 0
        ;;
    check|resources|summary)
        [ "$#" -eq 1 ] || { usage; exit 2; }
        if [ "$ACTION" = "check" ]; then
            ensure_runtime
        fi
        UBITECT_PROJECT="$PROJECT" UBITECT_CONTAINER="$CONTAINER" \
        UBITECT_IMAGE="$IMAGE" \
        exec "$HOST_PY" -I "$PROJECT/scripts/demo_host.py" "$ACTION"
        ;;
    source|compile|candidates|verify|constraints|compare) ;;
    *)
        say "unknown DEMO action: $ACTION" >&2
        usage
        exit 2
        ;;
esac

CASE="${2:-}"
[ -n "$CASE" ] || { say "missing case: tutorial or history" >&2; exit 2; }
[ "$#" -eq 2 ] || { usage; exit 2; }
case "$CASE" in
    tutorial) ;;
    example)
        say "note: 'example' is a compatibility alias for 'tutorial'; using tutorial."
        CASE="tutorial"
        ;;
    history) ;;
    *)
        say "unknown DEMO case: $CASE" >&2
        usage
        exit 2
        ;;
esac

stage_exec "$ACTION" "$CASE"
exit $?
