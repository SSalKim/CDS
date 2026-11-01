"""Package only tracked public files and compare them with the last published tree."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess


PUBLIC_DIRS = {"data", "fonts", "docs", "special_images"}
PUBLIC_SUFFIXES = {".html", ".css", ".js", ".json", ".ico", ".svg", ".png", ".jpg",
                   ".jpeg", ".webp", ".gif", ".txt", ".xml", ".webmanifest", ".map"}
CONTROL_PATHS = {"pages_deploy.py", ".github/workflows/pages.yml"}
REQUIRED_PATHS = {"index.html", "radar.html", "typhoon.html", "style.css",
                  "data/manifest.json", "data/status.json"}
MAX_SITE_BYTES = 1_000_000_000


def git(root, *args, **kwargs):
    return subprocess.run(["git", "-c", f"safe.directory={root.as_posix()}", *args],
                          cwd=root, check=True, capture_output=True, **kwargs).stdout


def is_public(path):
    parts = PurePosixPath(path).parts
    if not parts or any(p in {".", ".."} or p.startswith(".") for p in parts):
        return False
    return (parts[0] in PUBLIC_DIRS or
            len(parts) == 1 and PurePosixPath(path).suffix.lower() in PUBLIC_SUFFIXES)


def tracked_tree(root, ref="HEAD"):
    entries = []
    for record in git(root, "ls-tree", "-r", "-l", "-z", ref).split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid, size = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8")
        if is_public(path) or path in CONTROL_PATHS:
            if mode not in {"100644", "100755"} or kind != "blob":
                raise ValueError(f"Public file must be a regular tracked file: {path}")
            entries.append((path, mode, oid, int(size)))
    return sorted(entries)


def fingerprint(entries):
    content = json.dumps([(p, m, oid) for p, m, oid, _ in entries], separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def plan(root, compare_ref=None, force=False):
    entries = tracked_tree(root)
    public = [entry for entry in entries if is_public(entry[0])]
    missing = REQUIRED_PATHS - {entry[0] for entry in public}
    if missing:
        raise ValueError("Missing public entrypoints: " + ", ".join(sorted(missing)))
    size = sum(entry[3] for entry in public)
    if size > MAX_SITE_BYTES:
        raise ValueError(f"Public site exceeds the 1 GB deployment budget: {size}")
    revision = fingerprint(entries)
    previous = fingerprint(tracked_tree(root, compare_ref)) if compare_ref else None
    return {"needed": force or revision != previous, "revision": revision,
            "commit": git(root, "rev-parse", "HEAD").decode().strip(),
            "file_count": len(public), "bytes": size}, public


def prepare(root, destination, report, public, materialize=False):
    destination = destination.resolve()
    if destination == root or root in destination.parents:
        raise ValueError("Pages staging directory must be outside the checkout")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Pages staging directory must be empty")
    if materialize:
        # Request only static roots, root-level assets, and the packaging controls.
        patterns = [f"/{p}/" for p in sorted(PUBLIC_DIRS)]
        patterns.extend("/" + p for p, _, _, _ in public if "/" not in p)
        patterns.extend("/" + p for p in sorted(CONTROL_PATHS))
        git(root, "sparse-checkout", "set", "--no-cone", "--stdin",
            input=("\n".join(patterns) + "\n").encode())
    destination.mkdir(parents=True, exist_ok=True)
    for path, _, _, _ in public:
        source = root / path
        if source.is_symlink() or not source.is_file() or root not in source.resolve().parents:
            raise ValueError(f"Unsafe or missing public file: {path}")
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (destination / ".nojekyll").touch()
    (destination / "deployment.json").write_text(json.dumps({
        "commit": report["commit"], "site_revision": report["revision"],
    }, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--compare-ref")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--prepare", type=Path)
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.compare_ref and not re.fullmatch(r"[a-fA-F0-9]{40}", args.compare_ref):
        parser.error("--compare-ref must be a complete commit SHA")
    report, public = plan(root, args.compare_ref, args.force)
    if args.prepare:
        prepare(root, args.prepare, report, public, args.materialize)
    print(json.dumps(report, sort_keys=True))
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            for key, value in report.items():
                output.write(f"{key}={str(value).lower() if isinstance(value, bool) else value}\n")


if __name__ == "__main__":
    main()
