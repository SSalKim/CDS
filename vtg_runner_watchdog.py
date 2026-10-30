"""Release stalled automatic VTG runner queues without cancelling running work."""

import json
import os
import re
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen


WORKFLOW = "vtg.yml"
MAX_QUEUE_SECONDS = 180


class GitHub:
    def __init__(self, repository, token):
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository) or not token:
            raise ValueError("GitHub repository and token are required")
        self.repository = repository
        self.token = token

    def request(self, path, body=None):
        request = Request(
            f"https://api.github.com/repos/{self.repository}{path}",
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": "Bearer " + self.token,
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json",
                     "X-GitHub-Api-Version": "2022-11-28",
                     "User-Agent": "CDS-VTG-runner-watchdog"},
            method="POST" if body is not None else "GET",
        )
        try:
            with urlopen(request, timeout=20) as response:
                content = response.read(4 * 1024 * 1024 + 1)
        except HTTPError as exc:
            code = exc.code
            exc.close()
            raise RuntimeError(f"GitHub HTTP {code}: {path.split('?')[0]}") from None
        if len(content) > 4 * 1024 * 1024:
            raise ValueError("GitHub response exceeds size limit")
        return json.loads(content) if content else {}


def automatic_run(run, repository):
    return (run.get("path") == ".github/workflows/vtg.yml"
            and run.get("head_branch") == "main"
            and run.get("event") == "workflow_dispatch"
            and (run.get("head_repository") or {}).get("full_name") == repository
            and isinstance(run.get("run_number"), int)
            and run.get("display_title") == f"Generate VTG images {run['run_number']}")


def stale_self_hosted_job(job, now):
    if (job.get("name") != "generate" or job.get("status") != "queued"
            or not {"self-hosted", "cds-vtg"}.issubset(job.get("labels") or [])):
        return False
    try:
        created = datetime.fromisoformat(str(job.get("created_at", "")).replace("Z", "+00:00"))
        return (now - created).total_seconds() >= MAX_QUEUE_SECONDS
    except (TypeError, ValueError):
        return False


def recover_stalled_runs(client, *, now=None):
    now = now or datetime.now(timezone.utc)
    recovered = []
    dispatched = False
    for page in range(1, 11):
        runs = client.request(
            f"/actions/workflows/{WORKFLOW}/runs?status=queued&branch=main&per_page=100&page={page}"
        )["workflow_runs"]
        for run in runs:
            if run.get("status") != "queued" or not automatic_run(run, client.repository):
                continue
            jobs = client.request(f"/actions/runs/{int(run['id'])}/jobs?filter=latest&per_page=100")["jobs"]
            for job in jobs:
                if not stale_self_hosted_job(job, now):
                    continue
                # Recheck immediately before taking action: the laptop may have just resumed.
                current = client.request(f"/actions/jobs/{int(job['id'])}")
                if not stale_self_hosted_job(current, now):
                    continue
                if not dispatched:
                    # If dispatch fails, leave the original queue untouched for the next check.
                    client.request(f"/actions/workflows/{WORKFLOW}/dispatches", {
                        "ref": "main", "inputs": {"runner_mode": "github-hosted"},
                    })
                    dispatched = True
                client.request(f"/actions/runs/{int(run['id'])}/cancel", {})
                recovered.append(run["id"])
                print(f"Released stale self-hosted queue for VTG run {run['id']}; GitHub-hosted recovery dispatched.")
                break
        if len(runs) < 100:
            return recovered
    raise RuntimeError("Too many queued workflow pages; refusing an incomplete scan")


def main():
    client = GitHub(os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GH_TOKEN", ""))
    recovered = recover_stalled_runs(client)
    print(f"VTG watchdog: {len(recovered)} stale self-hosted queue(s) recovered.")


if __name__ == "__main__":
    main()
