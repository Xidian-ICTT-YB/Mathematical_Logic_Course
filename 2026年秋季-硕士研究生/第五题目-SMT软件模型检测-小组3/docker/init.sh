#!/bin/sh
set -eu

CG=/sys/fs/cgroup

# Move the initialization process out of the root cgroup.
mkdir -p "$CG/init" "$CG/benchexec"
echo $$ > "$CG/init/cgroup.procs"

# Enable controllers for BenchExec.
for controller in $(cat "$CG/cgroup.controllers"); do
    echo "+$controller" > "$CG/cgroup.subtree_control"
    echo "+$controller" > "$CG/benchexec/cgroup.subtree_control"
done

# Start the program from within the delegated subtree.
mkdir -p "$CG/benchexec/launcher"
echo $$ > "$CG/benchexec/launcher/cgroup.procs"

# Delegate the subtree to the non-root user.
chown -R benchuser:benchuser "$CG/benchexec"

exec runuser -u benchuser -- "$@"
