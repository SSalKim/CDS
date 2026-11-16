"""Wait at most three minutes for the shared laptop, then use GitHub-hosted."""
import argparse
import json
import os
import time
from urllib.request import Request, urlopen

HOSTED = "ubuntu-24.04"


def laptop(payload):
    for runner in payload.get("runners", []):
        labels = {str(item.get("name", "")).lower() for item in runner.get("labels", [])}
        if runner.get("status") == "online" and "cds-vtg" in labels and "linux" in labels:
            return runner
    return None


def chart_busy(payload):
    return any(runner.get("busy") and any(label.get("name", "").lower() == "cds-public-charts"
                                         for label in runner.get("labels", []))
               for runner in payload.get("runners", []))


def select(fetch, *, wait_seconds=180, clock=time.monotonic, sleep=time.sleep):
    deadline = clock() + wait_seconds
    while True:
        try:
            own = laptop(fetch("SSalKim/CDS", min(20, max(.1, deadline-clock()))))
            if own is None or clock() >= deadline:
                return HOSTED
            charts = fetch("SSalKim/CDS-Public-Charts", min(20, max(.1, deadline-clock())))
        except Exception as error:
            print("Shared runner status unavailable; using GitHub-hosted.", type(error).__name__, getattr(error, "code", None))
            return HOSTED
        if not own.get("busy", True) and not chart_busy(charts):
            return ["self-hosted", "cds-vtg"]
        remaining = deadline-clock()
        if remaining <= 0:
            return HOSTED
        print("Shared laptop busy; checking again shortly.", flush=True)
        sleep(min(10, remaining))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("auto", "github-hosted"), default="auto")
    args = parser.parse_args()
    result = HOSTED
    if args.mode == "auto":
        token = os.environ.get("GH_TOKEN", "")

        def fetch(repo, timeout):
            request = Request(f"https://api.github.com/repos/{repo}/actions/runners?per_page=100",
                              headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                                       "X-GitHub-Api-Version": "2022-11-28"})
            with urlopen(request, timeout=timeout) as response:
                return json.load(response)

        result = select(fetch)
    print("Selected VTG runner:", json.dumps(result))
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a", encoding="utf-8") as stream:
            stream.write("runner_kind=" + ("github-hosted" if result == HOSTED else "self-hosted") + "\n")
            stream.write("runner_labels=" + json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
