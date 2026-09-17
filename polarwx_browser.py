"""Read only the forecast response loaded by Polarwx's normal browser UI."""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


PAGE_URL = "https://polarwx.com/tropical/"


class PolarwxBrowserError(RuntimeError):
    pass


def request_identity(atcf_id: str, data_time: str) -> tuple[str, str]:
    storm = str(atcf_id).strip().lower()
    stamp = str(data_time).strip()
    if not re.fullmatch(r"[a-z]{2}\d{6}", storm):
        raise ValueError("Invalid Polarwx ATCF ID")
    if not re.fullmatch(r"\d{10}(00)?", stamp):
        raise ValueError("Invalid Polarwx cycle")
    cycle = stamp[:10]
    if datetime.strptime(cycle, "%Y%m%d%H").hour not in (0, 6, 12, 18):
        raise ValueError("Polarwx requires a 00/06/12/18 UTC cycle")
    return storm, cycle


def matches_cycle_response(url: str, atcf_id: str, cycle: str) -> bool:
    parsed = urlsplit(url)
    return (
        parsed.scheme == "https" and parsed.netloc == "polarwx.com"
        and parsed.path == f"/data/tropical/storms/{atcf_id}/ensembles/{cycle}.json"
    )


def capture_cycle(
    atcf_id: str,
    data_time: str,
    *,
    timeout_seconds: float = 30,
    artifacts_dir: Path | None = None,
    report: dict | None = None,
) -> str:
    from playwright.sync_api import sync_playwright

    storm, cycle = request_identity(atcf_id, data_time)
    report = report if report is not None else {}
    report.update(atcf_id=storm, cycle=cycle, mode="raw", timings={}, responses=[])
    started = time.monotonic()
    deadline = started + timeout_seconds
    timings = report["timings"]
    if artifacts_dir is not None:
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    def remaining_ms() -> int:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise PolarwxBrowserError("Browser collection deadline exceeded")
        return max(1, int(remaining * 1000))

    browser = page = None
    captured = []
    try:
        with sync_playwright() as playwright:
            try:
                stage = time.monotonic()
                browser = playwright.chromium.launch(headless=True, timeout=remaining_ms())
                page = browser.new_page(viewport={"width": 1500, "height": 950})
                timings["browser_start_seconds"] = round(time.monotonic() - stage, 3)

                def observe(response):
                    if matches_cycle_response(response.url, storm, cycle):
                        captured.append(response)
                        report["responses"].append({"status": response.status, "url": response.url})

                page.on("response", observe)
                stage = time.monotonic()
                navigation = page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=remaining_ms())
                report["page_status"] = navigation.status if navigation else None
                if navigation is None or not navigation.ok:
                    raise PolarwxBrowserError(f"Page returned HTTP {report['page_status']}")
                report["webdriver"] = page.evaluate("navigator.webdriver")
                timings["page_load_seconds"] = round(time.monotonic() - stage, 3)

                stage = time.monotonic()
                # These are visible site controls, not a direct request to a JSON URL.
                page.locator("button.sys-card").first.wait_for(state="visible", timeout=remaining_ms())
                storm_button = page.locator(f'button.sys-card[data-id="{storm}"]')
                if not storm_button.count():
                    raise PolarwxBrowserError("ATCF ID is not in the active-storm UI")
                storm_button.click(timeout=remaining_ms())
                page.get_by_role("tab", name="Models", exact=True).click(timeout=remaining_ms())
                page.get_by_role("button", name="Raw", exact=True).click(timeout=remaining_ms())
                page.get_by_role("button", name="View by cycle", exact=True).click(timeout=remaining_ms())
                picker = page.locator("#mcycle-select")
                picker.locator("option").first.wait_for(state="attached", timeout=remaining_ms())
                if not picker.locator(f'option[value="{cycle}"]').count():
                    raise PolarwxBrowserError("Requested cycle is not available in the UI")
                picker.select_option(cycle, timeout=remaining_ms())
                if picker.input_value(timeout=remaining_ms()) != cycle:
                    raise PolarwxBrowserError("Requested cycle was not selected")
                raw_button = page.get_by_role("button", name="Raw", exact=True)
                if "active" not in (raw_button.get_attribute("class", timeout=remaining_ms()) or "").split():
                    raise PolarwxBrowserError("Raw mode was not selected")
                report["selected_cycle"] = cycle
                timings["ui_selection_seconds"] = round(time.monotonic() - stage, 3)

                stage = time.monotonic()
                # The site may have prefetched this cycle before the dropdown changed.
                if not captured:
                    page.wait_for_event("response", predicate=lambda r: matches_cycle_response(r.url, storm, cycle), timeout=remaining_ms())
                response = captured[-1]
                if not response.ok:
                    raise PolarwxBrowserError(f"Page forecast response returned HTTP {response.status}")
                text = response.text()
                if not isinstance(json.loads(text), dict):
                    raise PolarwxBrowserError("Page forecast response is not a JSON object")
                timings["response_read_seconds"] = round(time.monotonic() - stage, 3)
                report["success"] = True
                if artifacts_dir is not None:
                    (artifacts_dir / "page-response.json").write_text(text, encoding="utf-8")
                return text
            finally:
                if page is not None and artifacts_dir is not None:
                    try:
                        page.screenshot(path=str(artifacts_dir / "page.png"), timeout=5000)
                    except Exception:
                        pass
                if browser is not None:
                    browser.close()
    except Exception as exc:
        report.update(success=False, error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        timings["total_seconds"] = round(time.monotonic() - started, 3)
        if artifacts_dir is not None:
            (artifacts_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atcf-id", required=True)
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    args = parser.parse_args()
    report: dict = {}
    try:
        text = capture_cycle(args.atcf_id, args.cycle, artifacts_dir=args.artifacts_dir, report=report)
        import VTG
        import requests

        settings = VTG.Settings(atcf_id=args.atcf_id, data_time=args.cycle[:10] + "00", fcst_hours=240,
                                http_cache_dir=args.artifacts_dir / "cache")
        frame = VTG.read_polarwx_json(text, settings, atcf_id=args.atcf_id)
        if frame.empty:
            raise PolarwxBrowserError("No usable VTG model points in browser response")
        frame.to_csv(args.artifacts_dir / "tracks.csv", index=False)
        report.update(models=int(frame["SRC"].nunique()), points=len(frame),
                      pressure_points=int(frame["PS"].gt(0).sum()))
        VTG.write_cached_text(VTG.http_cache_path(settings.http_cache_dir, VTG.polarwx_url(args.atcf_id, settings.data_time)), text)
        started = time.monotonic()
        cached_frame = VTG.fetch_polarwx_data(requests.Session(), settings)
        report["timings"]["warm_cache_seconds"] = round(time.monotonic() - started, 3)
        if not frame.equals(cached_frame):
            raise PolarwxBrowserError("Cached source differs from browser response")
    except Exception as exc:
        report.update(success=False, error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        args.artifacts_dir.mkdir(parents=True, exist_ok=True)
        (args.artifacts_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
