"""Validate and record the shared VTG rendering environment, without credentials."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PYTHON_VERSION = "3.12.15"
LOCK = ROOT / "requirements-vtg.lock.txt"
FONT = ROOT / "fonts" / "NanumSquareB.ttf"


def pinned_versions():
    return dict(line.strip().split("==", 1) for line in LOCK.read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#"))


@lru_cache(maxsize=1)
def runtime_report():
    packages = {}
    for name in pinned_versions():
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    result = {"python": platform.python_version(), "packages": packages,
              "lock_sha256": hashlib.sha256(LOCK.read_bytes()).hexdigest(),
              "font_sha256": hashlib.sha256(FONT.read_bytes()).hexdigest()}
    if packages.get("matplotlib"):
        import matplotlib
        from matplotlib import ft2font
        result.update(backend=matplotlib.get_backend(), freetype=ft2font.__freetype_version__)
    return result


def check_runtime(report=None):
    report = runtime_report() if report is None else report
    errors = []
    if report["python"] != PYTHON_VERSION:
        errors.append(f"Python {report['python']} != {PYTHON_VERSION}")
    for name, expected in pinned_versions().items():
        if report["packages"].get(name) != expected:
            errors.append(f"{name} {report['packages'].get(name)} != {expected}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = runtime_report()
    if args.check:
        errors = check_runtime(report)
        if errors:
            raise SystemExit("Render environment mismatch: " + "; ".join(errors))
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
