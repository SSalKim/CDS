"""Bounded public-model chart production with isolated Drive publication."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess

from public_charts import policy

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "data/public_charts_manifest.json"


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    temporary.replace(path)


def manifest_bytes(payload):
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def resolve_plan(models, cycle=None, requested_hours=None, now=None):
    result = []
    for model in models:
        cycles = [cycle] if cycle else policy.cycle_candidates(model, now)
        for selected in cycles:
            from public_charts.dates import parse_cycle
            if parse_cycle(selected).hour % policy.CYCLE_STEP[model] and len(models)>1:
                continue
            for hour in requested_hours if requested_hours is not None else policy.hours(model):
                policy.expected_keys(model, selected, hour)
                result.append({"model": model, "cycle": selected, "hour": hour})
    return result


def recover_rows(inventory):
    rows = {}
    for item in inventory:
        props = item.get("appProperties", {})
        if props.get("kind") != "image":
            continue
        match = policy.KEY_PATTERN.fullmatch(props.get("key", ""))
        if not match:
            raise ValueError("Unrecognized managed image; automatic cleanup refused")
        model, cycle, hour, product, domain = match.groups()
        entry_key = policy.key(model, cycle, int(hour), product, domain)
        if entry_key not in policy.expected_keys(model, cycle, int(hour)):
            raise ValueError("Unexpected managed product; automatic cleanup refused")
        file_id = item["id"]
        sha = props.get("sha256", "")
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("Managed image lacks a valid input-independent content hash")
        row = {"model": model, "cycle": cycle, "hour": int(hour), "product": product, "domain": domain,
               "file_id": file_id, "size": int(item["size"]), "sha256": sha,
               "url": f"https://drive.usercontent.google.com/download?id={file_id}&export=view&authuser=0"}
        rows.setdefault(entry_key, row)
    return rows


def cleanup_raw(work):
    work = Path(work).resolve()
    root = work / "raw-cache"
    if root.is_symlink() or root.resolve().parent != work:
        raise ValueError("Unsafe scratch root")
    for name in ("grib-cache", "fields", "extended-fields", "images"):
        target = root / name
        if target.is_symlink() or target.resolve().parent != root:
            raise ValueError("Unsafe scratch directory")
        if target.exists():
            shutil.rmtree(target)


def plan_cleanup(rows, inventory, budget, reserve_bytes=0):
    if reserve_bytes >= budget:
        raise ValueError("One incoming image exceeds the image budget")
    kept, _ = policy.retain(rows, budget - reserve_bytes)
    retained = {row["file_id"] for row in kept}
    candidates = {item["id"] for item in inventory if item.get("appProperties", {}).get("kind") == "image"}
    candidates.update(row["file_id"] for row in rows)
    return kept, sorted(candidates - retained)


def finalize_cleanup(store, manifest, plan, published_payload, *, grace_seconds=600, now=None, max_files=300):
    if plan.get("namespace") != "cds-public-charts-v1" or plan.get("folder_id") != store.folder_id:
        raise ValueError("Cleanup target does not match the isolated chart folder")
    digest = hashlib.sha256(manifest_bytes(manifest)).hexdigest()
    if digest != plan.get("manifest_sha256") or manifest != published_payload:
        raise ValueError("The exact retained manifest must be published before cleanup")
    if store.read_json("manifest.json", {}) != manifest:
        raise ValueError("Drive manifest changed; stale cleanup refused")
    retained = {row["file_id"] for row in manifest["charts"]}
    pending = list(plan.get("delete_ids", []))
    if len(pending) != len(set(pending)) or retained.intersection(pending):
        raise ValueError("Cleanup plan references retained or duplicate files")
    inventory = {item["id"]: item for item in store.inventory()}
    if any(file_id in inventory and inventory[file_id].get("appProperties", {}).get("kind") != "image" for file_id in pending):
        raise ValueError("Only generated image files can be removed")
    state = store.read_json("state.json", {})
    deadlines = state.get("pending_delete_after", {})
    timestamp = now if now is not None else datetime.now(timezone.utc).timestamp()
    remaining = {}
    removed = 0
    for file_id in pending:
        if file_id not in inventory:
            continue
        deadline = deadlines.get(file_id, timestamp + grace_seconds)
        if timestamp >= deadline and removed < max_files:
            store.delete_managed(file_id)
            removed += 1
        else:
            remaining[file_id] = deadline
    state["pending_delete_after"] = remaining
    state["pending_delete_ids"] = []
    store.write_json("state.json", state)
    return removed


def verify_public_url(url):
    import requests
    # Do not reuse the authenticated Drive session for this check.
    with requests.get(url, headers={"Range": "bytes=0-15"}, stream=True, timeout=(15, 45)) as response:
        response.raise_for_status()
        header = next(response.iter_content(chunk_size=16), b"")
        if header[:4] != b"RIFF" or header[8:12] != b"WEBP":
            raise ValueError("Anonymous Drive URL did not return a WebP image")


def run(args, store=None):
    plan = resolve_plan(args.models, args.cycle, args.hours)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "retention": policy.RETENTION,
                          "products": "nine seasonal products; Asia surfce only; Korea rain/snow layouts",
                          "candidates": plan, "max_leads_per_model": args.max_leads}, indent=2))
        return 0
    from public_charts.producer import produce_lead
    work = Path(args.workdir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    if work == ROOT or work == work.parent:
        raise ValueError("A dedicated work directory is required")
    local = args.local
    if local:
        output = work / "preview"
        output.mkdir(parents=True, exist_ok=True)
        state = read_json(output / "manifest.json", {"charts": []})
        inventory = []
    else:
        from public_charts_drive import ChartDriveStore
        store = store or ChartDriveStore.from_environment()
        store.verify_account_and_folder()
        state = store.read_json("state.json", {"schema_version": 1, "rows": []})
        if state.get("schema_version") != 1:
            raise ValueError("Unknown private production state version")
        inventory = store.inventory()
    rows = {policy.row_key(row): row for row in state.get("rows", state.get("charts", []))}
    if not local:
        recover_rows(inventory)
        valid_ids = {item["id"] for item in inventory}
        rows = {key: row for key, row in rows.items() if row.get("file_id") in valid_ids}
        # Uncommitted uploads are not public state. A retry reuses and verifies
        # them through upload_image rather than trusting their metadata alone.
    if not args.cycle:
        planned={(item["model"],item["cycle"]) for item in plan}
        for model in args.models:
            previous=sorted({row["cycle"] for row in rows.values() if row["model"]==model},reverse=True)[:policy.RETENTION[model]]
            for cycle in previous:
                if (model,cycle) not in planned:
                    plan.extend({"model":model,"cycle":cycle,"hour":hour} for hour in policy.hours(model))
    image_bytes = policy.unique_bytes(rows.values())
    if not local:
        image_bytes = sum(int(item.get("size", 0)) for item in inventory
                          if item.get("appProperties", {}).get("kind") == "image")
    counts = {model: 0 for model in args.models}
    errors = []
    verified_cycles = set(state.get("verified_cycles", []))
    attempts = 0
    unavailable_cycles = set()
    cycle_misses = {}
    budget_blocked = False
    reserve_bytes = 0
    raw_root = Path(args.cache_root).resolve() if args.cache_root else work / "raw-cache"
    before_ids = {item["id"] for item in inventory} | {row["file_id"] for row in rows.values()}

    def save_state():
        if local:
            write_json(output / "manifest.json", policy.public_manifest(list(rows.values())))
        else:
            store.write_json("state.json", {"schema_version": 1, "pipeline_version": policy.PIPELINE_VERSION,
                             "rows": list(rows.values()), "errors": errors[-40:],
                             "verified_cycles": sorted(verified_cycles),
                             "pending_delete_after": state.get("pending_delete_after", {})})

    try:
        for target in plan:
            model, cycle, hour = target["model"], target["cycle"], target["hour"]
            if counts[model] >= args.max_leads:
                continue
            if (model, cycle) in unavailable_cycles:
                continue
            if not args.force and policy.expected_keys(model, cycle, hour) <= rows.keys():
                continue
            attempts += 1
            if attempts > args.max_leads * len(args.models) * 4:
                break

            def publish(product, domain, path, alias_of=None):
                nonlocal image_bytes, reserve_bytes
                entry_key = policy.key(model, cycle, hour, product, domain)
                if alias_of:
                    source = rows[policy.key(model, cycle, hour, *alias_of)]
                    info = {key: source[key] for key in ("file_id", "url", "size", "sha256")}
                elif local:
                    destination = output / "images" / model / path.name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, destination)
                    info = {"file_id": entry_key, "url": destination.relative_to(output).as_posix(),
                            "size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                else:
                    if image_bytes + path.stat().st_size > args.max_bytes:
                        reserve_bytes = max(reserve_bytes, path.stat().st_size)
                        raise OverflowError("Image budget reached; publish retention cleanup before continuing")
                    info = store.upload_image(path, entry_key)
                    if f"{model}/{cycle}" not in verified_cycles:
                        verify_public_url(info["url"])
                        verified_cycles.add(f"{model}/{cycle}")
                    if info["file_id"] not in before_ids:
                        image_bytes += int(info["size"])
                        before_ids.add(info["file_id"])
                rows[entry_key] = {"model": model, "cycle": cycle, "hour": hour, "product": product,
                                   "domain": domain, **{key: info[key] for key in ("file_id", "url", "size", "sha256")}}

            try:
                result = produce_lead(model, cycle, hour, raw_root, rows.keys(), publish, force=args.force)
                counts[model] += 1
                print(json.dumps({**target, **result}), flush=True)
                save_state()
            except OverflowError as error:
                budget_blocked = True
                errors.append({**target, "status": "budget", "error": str(error)})
                break
            except Exception as error:
                from public_charts.sources import NotReady
                if isinstance(error, NotReady):
                    cycle_misses[model, cycle] = cycle_misses.get((model, cycle), 0) + 1
                    if hour == 0 or cycle_misses[model, cycle] >= 2:
                        unavailable_cycles.add((model, cycle))
                errors.append({**target, "status": "pending" if isinstance(error, NotReady) else "error",
                               "error": type(error).__name__})
                print(json.dumps(errors[-1]), flush=True)
                if args.fail_fast and not isinstance(error, NotReady):
                    raise
            finally:
                if not local:
                    cleanup_raw(work)
    finally:
        save_state()
    if local:
        manifest = policy.public_manifest(list(rows.values()))
        write_json(output / "manifest.json", manifest)
        cards = "".join(f'<figure><figcaption>{html.escape(policy.row_key(row))}</figcaption>'
                        f'<img style="max-width:100%" src="{html.escape(row["url"])}"></figure>'
                        for row in rows.values())
        (output / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>Public chart preview</title>' + cards, encoding="utf-8")
        print(f"Local preview: {output / 'index.html'}")
        return int(any(row["status"] == "error" for row in errors))
    kept, delete_ids = plan_cleanup(list(rows.values()), inventory, args.max_bytes, reserve_bytes)
    manifest = policy.public_manifest(kept)
    previous = read_json(args.manifest, {})
    if previous.get("charts") == manifest["charts"] and previous.get("models") == manifest["models"]:
        manifest = previous
    store.write_json("manifest.json", manifest)
    write_json(args.manifest, manifest)
    write_json(work / "cleanup-plan.json", {"namespace": "cds-public-charts-v1", "folder_id": store.folder_id,
               "manifest_sha256": hashlib.sha256(manifest_bytes(manifest)).hexdigest(), "delete_ids": delete_ids})
    print(json.dumps({"rendered_leads": counts, "retained_bytes": policy.unique_bytes(kept),
                      "pending_delete_files": len(delete_ids), "budget_wait": budget_blocked, "errors": errors[-40:]}))
    return int(any(row["status"] == "error" for row in errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", choices=policy.RETENTION, default=list(policy.RETENTION))
    parser.add_argument("--cycle")
    parser.add_argument("--hours", nargs="+", type=int)
    parser.add_argument("--max-leads", type=int, default=2)
    parser.add_argument("--max-bytes", type=int, default=policy.MAX_IMAGE_BYTES)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--workdir", type=Path, default=ROOT / "outputs/public-charts-work")
    parser.add_argument("--cache-root", help="Only for explicit local preview; production scratch is isolated")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--check-drive", action="store_true")
    parser.add_argument("--finalize-cleanup", action="store_true")
    args = parser.parse_args()
    if args.max_leads < 1 or args.max_bytes < 1 or args.cache_root and not args.local:
        parser.error("Invalid batch/budget; cache-root is local-only")
    if args.check_drive or args.finalize_cleanup:
        from public_charts_drive import ChartDriveStore
        store = ChartDriveStore.from_environment()
        if args.check_drive:
            store.verify_account_and_folder()
            print("Dedicated Drive account and owned folder verified; no files changed.")
            return 0
        published = subprocess.check_output(["git", "-c", f"safe.directory={ROOT.as_posix()}", "show",
                                             "origin/main:data/public_charts_manifest.json"], cwd=ROOT)
        count = finalize_cleanup(store, read_json(args.manifest, {}),
                                 read_json(args.workdir / "cleanup-plan.json", {}), json.loads(published))
        print(f"Permanently removed {count} superseded managed images after publication.")
        return 0
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
