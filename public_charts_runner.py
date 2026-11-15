"""Select only an explicitly matching, online and idle VTG laptop runner."""
import argparse
import json
import os
from urllib.request import Request, urlopen


def choose(payload):
    for runner in payload.get("runners", []):
        labels = {str(label.get("name", "")).lower() for label in runner.get("labels", [])}
        if runner.get("status") == "online" and not runner.get("busy", True) and "cds-vtg" in labels and "linux" in labels:
            return ["self-hosted", "linux", "cds-vtg"]
    return "ubuntu-24.04"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("auto", "github-hosted"), default="auto")
    args = parser.parse_args()
    result = "ubuntu-24.04"
    if args.mode == "auto":
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        token = os.environ.get("GH_TOKEN", "")
        if repository and token:
            try:
                request = Request(f"https://api.github.com/repos/{repository}/actions/runners?per_page=100",
                                  headers={"Authorization": "Bearer " + token,
                                           "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
                with urlopen(request, timeout=20) as response:
                    result = choose(json.load(response))
            except Exception:
                print("Runner status unavailable; using GitHub-hosted.")
    print("Selected runner:", json.dumps(result))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write("labels=" + json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
