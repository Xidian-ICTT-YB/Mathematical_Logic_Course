# Example optional configuration.  The scripts work without sourcing this file;
# export any value you need before running REPRODUCE.sh / RUN_HISTORY.sh / DEMO.sh.
#
# Linux/amd64 image tag and persistent demo container name.  Use distinct values
# for an independent acceptance copy so it cannot reuse another copy's state.
export UBITECT_IMAGE="ubitect-repro-delivery:base"
export UBITECT_CONTAINER="ubitect-repro-delivery-demo"

# Reuse a directory that already contains the two pinned archives.  Files are
# accepted only when their SHA-256 matches scripts/fetch_dependencies.sh.
# export UBITECT_DOWNLOAD_CACHE="/path/to/verified/downloads"

# Run identifiers (default: UTC timestamp).
# export UBITECT_RUN_ID="RUN-20261112T000000Z"
# export UBITECT_HISTORY_RUN_ID="HIST-20261112T000000Z"

# Docker Desktop location on macOS (default shown).
# export UBITECT_DOCKER_APP="/Applications/Docker.app"

# Force a rebuild of the image or of the in-container toolchain.
# export UBITECT_REBUILD_IMAGE=1
# export FORCE_BUILD=1

# Optional alternative source checkout fetched by scripts/fetch_upstream_source.sh.
# export UBITECT_SOURCE="$PWD/source/UBITect-upstream"
