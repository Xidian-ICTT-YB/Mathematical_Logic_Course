# Commands used for this acceptance run

```bash
cd <extracted-project>
UBITECT_IMAGE=ubitect-repro-delivery-20261112b:base \
UBITECT_RUN_ID=RUN-20261112T075709Z \
UBITECT_HISTORY_RUN_ID=HIST-20261112T075709Z \
./REPRODUCE_ALL.sh
```

The script's own stage log is preserved in the project at `logs/` and
the selected stage records are copied into `evidence/logs/`.

Per-stage exit codes are in `evidence/logs/stage-exit-codes.txt`;
the image ID and platform are in `evidence/logs/image-id.txt` and
`evidence/logs/image-platform.txt`.
