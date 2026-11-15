"""Prepare the fixed chart map cache and prune only derived checkpoints."""
import argparse
from pathlib import Path
import re
import shutil

from public_charts.policy import RETENTION


def prune_checkpoints(root):
    root = Path(root).resolve()
    models = {model: [] for model in RETENTION}
    if not root.exists():
        return
    for directory in root.iterdir():
        if directory.is_symlink() or not directory.is_dir() or not re.fullmatch(r"\d{10}", directory.name):
            raise ValueError("Unexpected checkpoint directory")
        for model in RETENTION:
            if (directory / model).is_dir():
                models[model].append(directory.name)
    for model, cycles in models.items():
        for cycle in sorted(cycles, reverse=True)[RETENTION[model] + 1:]:
            target = root / cycle / model
            if target.is_symlink() or not target.resolve().is_relative_to(root):
                raise ValueError("Unsafe derived checkpoint path")
            shutil.rmtree(target)
    for directory in root.iterdir():
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-maps", action="store_true")
    parser.add_argument("--prune-checkpoints", type=Path)
    args = parser.parse_args()
    if args.prepare_maps:
        import public_charts.plotter
        from cartopy.io import shapereader
        for resolution, category, name in (("50m", "physical", "land"),
                                            ("10m", "physical", "coastline"),
                                            ("50m", "cultural", "admin_0_boundary_lines_land"),
                                            ("10m", "cultural", "admin_1_states_provinces")):
            shapereader.natural_earth(resolution=resolution, category=category, name=name)
    if args.prune_checkpoints:
        prune_checkpoints(args.prune_checkpoints)


if __name__ == "__main__":
    main()
