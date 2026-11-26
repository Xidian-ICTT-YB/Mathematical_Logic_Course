"""Check the SHA-256 of the files listed in MANIFEST.sha256."""

import hashlib
from pathlib import Path


def sha256_file(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    evidence = root / "evidence"
    manifest = root / "MANIFEST.sha256"
    checked = set()
    errors = []

    for number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        digest, separator, name = line.partition("  ")
        if not separator or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            errors.append(f"清单格式有误，第 {number} 行")
            continue
        path = (root / name).resolve()
        if evidence not in path.parents or path in checked:
            errors.append(f"清单路径有误或重复：{name}")
            continue
        checked.add(path)
        if not path.is_file():
            errors.append(f"缺少文件：{name}")
        elif sha256_file(path) != digest:
            errors.append(f"校验值不同：{name}")

    if not checked:
        errors.append("清单为空")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"{len(checked)} 个证据文件的 SHA-256 与清单一致。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
