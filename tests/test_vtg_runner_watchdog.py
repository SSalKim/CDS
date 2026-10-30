import unittest
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import Mock

import vtg_runner_watchdog as watchdog


NOW = datetime(2026, 10, 30, 22, 25, tzinfo=timezone.utc)
RUN = {"id": 123, "path": ".github/workflows/vtg.yml", "head_branch": "main",
       "head_repository": {"full_name": "SSalKim/CDS"}, "event": "workflow_dispatch",
       "run_number": 12, "display_title": "Generate VTG images 12", "status": "queued"}
JOB = {"id": 456, "name": "generate", "status": "queued", "created_at": "2026-10-30T22:20:00Z",
       "labels": ["self-hosted", "cds-vtg"]}


class RunnerWatchdogTests(unittest.TestCase):
    def client(self, *, runs=None, jobs=None, current=None, dispatch_error=False):
        client = Mock(repository="SSalKim/CDS")

        def request(path, body=None):
            if "/runs?" in path:
                return {"workflow_runs": [deepcopy(RUN)] if runs is None else runs}
            if "/jobs?" in path:
                return {"jobs": [deepcopy(JOB)] if jobs is None else jobs}
            if path == "/actions/jobs/456":
                return deepcopy(JOB) if current is None else current
            if path.endswith("/dispatches") and dispatch_error:
                raise RuntimeError("dispatch failed")
            return {}

        client.request.side_effect = request
        return client

    def test_stale_automatic_queue_dispatches_before_cancelling(self):
        client = self.client()
        self.assertEqual([123], watchdog.recover_stalled_runs(client, now=NOW))
        writes = [(c.args[0], c.args[1]) for c in client.request.call_args_list if len(c.args) == 2]
        self.assertEqual([
            ("/actions/workflows/vtg.yml/dispatches", {"ref": "main", "inputs": {"runner_mode": "github-hosted"}}),
            ("/actions/runs/123/cancel", {}),
        ], writes)

    def test_recent_queue_is_left_alone(self):
        job = {**JOB, "created_at": "2026-10-30T22:24:00Z"}
        client = self.client(jobs=[job])
        self.assertEqual([], watchdog.recover_stalled_runs(client, now=NOW))
        self.assertEqual(2, client.request.call_count)

    def test_running_or_hosted_or_other_job_is_never_cancelled(self):
        for changes in ({"status": "in_progress"}, {"labels": ["ubuntu-latest"]}, {"name": "decide-runner"}):
            with self.subTest(changes=changes):
                client = self.client(jobs=[{**JOB, **changes}])
                self.assertEqual([], watchdog.recover_stalled_runs(client, now=NOW))
                self.assertEqual(2, client.request.call_count)

    def test_job_that_starts_during_inspection_is_not_cancelled(self):
        client = self.client(current={**JOB, "status": "in_progress"})
        self.assertEqual([], watchdog.recover_stalled_runs(client, now=NOW))
        self.assertEqual(3, client.request.call_count)

    def test_manual_backfill_other_branch_and_fork_are_left_alone(self):
        for changes in ({"display_title": "Generate VTG images 2026103012"},
                        {"display_title": "Generate VTG images 12 (manual)"},
                        {"path": ".github/workflows/vtg_backfill.yml"},
                        {"head_branch": "other"}, {"event": "pull_request"},
                        {"head_repository": {"full_name": "other/CDS"}}):
            with self.subTest(changes=changes):
                client = self.client(runs=[{**RUN, **changes}])
                self.assertEqual([], watchdog.recover_stalled_runs(client, now=NOW))
                self.assertEqual(1, client.request.call_count)

    def test_failed_recovery_dispatch_does_not_cancel_original(self):
        client = self.client(dispatch_error=True)
        with self.assertRaisesRegex(RuntimeError, "dispatch failed"):
            watchdog.recover_stalled_runs(client, now=NOW)
        self.assertFalse(any(c.args[0].endswith("/cancel") for c in client.request.call_args_list))

    def test_invalid_or_future_timestamp_is_not_a_stale_job(self):
        for timestamp in (None, "invalid", "2026-10-30T22:20:00", "2026-10-31T00:00:00Z"):
            with self.subTest(timestamp=timestamp):
                self.assertFalse(watchdog.stale_self_hosted_job({**JOB, "created_at": timestamp}, NOW))

    def test_no_waiting_runs_has_no_side_effects(self):
        client = self.client(runs=[])
        self.assertEqual([], watchdog.recover_stalled_runs(client, now=NOW))
        self.assertEqual(1, client.request.call_count)


if __name__ == "__main__":
    unittest.main()
