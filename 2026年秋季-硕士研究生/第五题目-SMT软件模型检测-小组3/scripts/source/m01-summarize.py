import bz2
import csv
import glob
import os
import sys
import xml.etree.ElementTree as ET

plan_path, result_root, output_csv = sys.argv[1:4]

with open(plan_path, encoding="utf-8-sig", newline="") as f:
    runs = list(csv.DictReader(f))

fields = [
    "run_id", "task_id", "algorithm", "expected",
    "status", "classification",
    "cpu_s", "wall_s", "memory",
    "source_sha256", "config_sha256",
    "raw_result", "output_dir"
]

records = []

for item in runs:
    folder = os.path.join(
        result_root, item["task_id"], item["algorithm"]
    )

    marker = os.path.join(folder, "run-complete.txt")

    record = {
        "run_id": item["run_id"],
        "task_id": item["task_id"],
        "algorithm": item["algorithm"],
        "expected": item["expected"],
        "status": "PENDING",
        "classification": "",
        "cpu_s": "",
        "wall_s": "",
        "memory": "",
        "source_sha256": item["source_sha256"],
        "config_sha256": item["config_sha256"],
        "raw_result": "",
        "output_dir": item["output_dir"],
    }

    files = sorted(glob.glob(
        os.path.join(folder, "benchexec", "*.xml.bz2")
    ))

    if os.path.isfile(marker):
        if len(files) != 1:
            record["status"] = "PARSE_ERROR"
            record["classification"] = "raw_result_missing_or_ambiguous"
        else:
            path = files[0]
            record["raw_result"] = os.path.relpath(
                path, os.path.dirname(result_root)
            ).replace("\\", "/")

            try:
                with bz2.open(path, "rb") as f:
                    root = ET.parse(f).getroot()

                run = root.find(".//run")

                if run is None:
                    raise ValueError("No run element")

                columns = {
                    col.attrib.get("title", "").lower():
                    col.attrib.get("value", "")
                    for col in run.findall("column")
                }

                status = columns.get("status", "")
                record["status"] = status or "UNKNOWN"

                def number(value):
                    value = value.strip()
                    if value.endswith("s"):
                        return value[:-1]
                    return value

                record["cpu_s"] = number(
                    columns.get("cputime", "")
                )
                record["wall_s"] = number(
                    columns.get("walltime", "")
                )
                record["memory"] = columns.get("memory", "")

                expected = item["expected"].upper()
                actual = status.lower()

                if actual == "true":
                    record["classification"] = (
                        "correct" if expected == "TRUE"
                        else "incorrect"
                    )
                elif actual.startswith("false"):
                    record["classification"] = (
                        "correct" if expected == "FALSE"
                        else "incorrect"
                    )
                else:
                    record["classification"] = "unresolved"

            except Exception as exc:
                record["status"] = "PARSE_ERROR"
                record["classification"] = str(exc)[:200]

    elif os.path.isdir(folder):
        record["status"] = "INCOMPLETE"

    records.append(record)

os.makedirs(os.path.dirname(output_csv), exist_ok=True)

with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)

finished = sum(
    x["status"] not in ("PENDING", "INCOMPLETE", "PARSE_ERROR")
    for x in records
)

print("Parsed {}/{} results".format(finished, len(records)))
print("CSV: {}".format(output_csv))