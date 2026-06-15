from __future__ import annotations

import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_ROOT / "VTG_IMG"

# Cycles where the exact TD->TYP transition could have been rendered under TD_*.
TRANSITION_CYCLES = """
2022040800 2022063000 2022070100 2022080906 2022081118 2022082812 2022090800 2022091200 2022091318 2022092300
2022092306 2022092600 2022092812 2022101406 2022101506 2022102700 2022111212 2022121112
2023042006 2023052006 2023060612 2023071506 2023072100 2023072718 2023080800 2023082400 2023082418
2023082800 2023083012 2023090512 2023092918 2023101706 2023121700
""".split()


def remove_path(path: Path) -> None:
    if path.is_file():
        print(f"delete file: {path}")
        path.unlink()
    elif path.is_dir():
        print(f"delete dir : {path}")
        shutil.rmtree(path)


def main() -> None:
    metadata_dir = OUTPUT_ROOT / "metadata"
    if not metadata_dir.exists():
        print(f"metadata directory not found: {metadata_dir}")
        return

    removed_dirs: set[Path] = set()
    for cycle in TRANSITION_CYCLES:
        data_time = f"{cycle}00"
        for meta_path in sorted(metadata_dir.glob(f"{data_time}_td_*h.json")):
            try:
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"skip unreadable metadata {meta_path}: {exc}")
                continue
            linked_typ = metadata.get("linked_typ_number")
            stage = str(metadata.get("storm_stage") or "").upper()
            if not linked_typ and stage != "TD":
                continue
            image_path_text = str(metadata.get("image_path") or "").strip()
            if image_path_text:
                image_path = Path(image_path_text)
                if not image_path.is_absolute():
                    image_path = PROJECT_ROOT / image_path
                if image_path.exists():
                    parent = image_path.parent
                    remove_path(image_path)
                    removed_dirs.add(parent)
            remove_path(meta_path)

    for directory in sorted(removed_dirs, key=lambda item: len(item.parts), reverse=True):
        try:
            if directory.exists() and not any(directory.iterdir()):
                remove_path(directory)
        except OSError as exc:
            print(f"skip directory cleanup {directory}: {exc}")

    print("done. Now force-rerun the listed transition cycles with the patched vtg_auto.py.")


if __name__ == "__main__":
    main()
