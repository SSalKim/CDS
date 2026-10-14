import gzip
import hashlib
import io
import json
import tempfile
import unittest
import urllib.request
import zipfile
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import VTG
import vtg_source_backup as backup


CYCLE = "202610140600"
NOW = datetime(2026, 10, 14, 16, tzinfo=timezone.utc)
STORM = "td_2026_57"


def rows(model="GFS", source="KNACKWX", leads=(0, 6, 12), *, cycle=CYCLE, latitude=16.0):
    initial = backup.cycle_time(cycle)
    return pd.DataFrame([{
        "FT": int(lead > 0), "YY": initial.year, "TYP": 57, "SEQ": 0, "TMD": lead,
        "TYP_TM(UTC)": cycle, "FT_TM(UTC)": (initial + timedelta(hours=lead)).strftime("%Y%m%d%H%M"),
        "LAT": latitude + lead / 60, "LON": 151 - lead / 60, "WS": 15, "PS": 1005,
        "SRC": model, VTG.DATA_SOURCE_COLUMN: source, VTG.RAW_MODEL_COLUMN: model,
    } for lead in leads])


def payload(key=STORM, cycle=CYCLE, aliases=None):
    return {"version": 1, "storm_key": key, "storm_keys": aliases or [key], "cycle": cycle, "rows": []}


def artifact_zip(root):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for path in root.rglob("*"):
            if path.is_file():
                archive.writestr(path.relative_to(root).as_posix(), path.read_bytes())
    return stream.getvalue()


class BackupMergeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.settings = VTG.Settings(
            storm_stage="TD", typ_number=57, storm_year="2026", data_time=CYCLE,
            atcf_id="wp962026", fcst_hours=240, source_backup_dir=Path(self.temp.name),
        )
        self.recent = patch.object(VTG, "recent_cycle", side_effect=lambda cycle: backup.recent_cycle(cycle, NOW))
        self.recent.start()
        self.addCleanup(self.recent.stop)

    def merge(self, frame, settings=None):
        with redirect_stdout(io.StringIO()):
            return VTG.merge_source_backups(frame, settings or self.settings)

    def test_deleted_invest_restores_same_cycle_after_renumbering(self):
        original = rows()
        self.merge(original)
        changed = replace(self.settings, atcf_id="wp292026")
        recovered = self.merge(original.iloc[:0], changed)
        self.assertEqual([0, 6, 12], recovered.TMD.tolist())
        self.assertTrue(recovered["_SOURCE_BACKUP"].all())

    def test_live_track_wins_whole_without_appending_backup_tail(self):
        self.merge(rows(leads=(0, 6, 12, 18, 24)))
        live = rows(leads=(0, 6, 12), latitude=17)
        result = self.merge(live)
        self.assertEqual([0, 6, 12], result.TMD.tolist())
        self.assertEqual(17, result.LAT.iloc[0])
        self.assertEqual(3, len(backup.read_snapshot(self.settings.source_backup_dir, STORM, CYCLE)["rows"]))

    def test_model_and_provider_priorities_are_preserved(self):
        self.merge(rows(source="APIHUB"))
        live = pd.concat([rows(source="KNACKWX", latitude=17), rows(model="ICON", source="POLARWX")])
        result = self.merge(live)
        with redirect_stdout(io.StringIO()):
            selected = VTG.select_model_sources_by_priority(result, self.settings)
        self.assertEqual({"APIHUB"}, set(selected[selected.SRC.eq("GFS")][VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual({"GFS", "ICON"}, set(selected.SRC))

    def test_enabling_empty_backup_preserves_normal_render_input(self):
        raw = pd.concat([rows(model="KMA", source="APIHUB"), rows(source="APIHUB"),
                         rows(source="KNACKWX", latitude=17), rows(model="ICON", source="POLARWX")], ignore_index=True)
        empty = raw.iloc[:0]
        with redirect_stdout(io.StringIO()):
            expected = VTG.normalize_track_data(raw, empty, empty, empty, VTG.empty_atcf_frame(), self.settings)
            collected = VTG.source_availability_frame(raw, empty, empty, empty, VTG.empty_atcf_frame(), self.settings)
            actual = VTG.normalize_guidance_frame(self.merge(collected), self.settings)
        columns = sorted(expected.columns)
        self.assertTrue(expected[list(set(columns) - set(actual.columns))].isna().all().all())
        pd.testing.assert_frame_equal(expected[columns], actual.reindex(columns=columns), check_dtype=False)

    def test_backup_payload_does_not_persist_urls_or_credentials(self):
        raw = rows().assign(url="https://example.invalid/?authKey=PRIVATE", authKey="PRIVATE")
        self.merge(raw)
        stored = backup.read_snapshot(self.settings.source_backup_dir, STORM, CYCLE)
        self.assertNotIn("PRIVATE", json.dumps(stored))
        self.assertNotIn("url", stored["rows"][0])

    def test_analysis_only_response_does_not_erase_forecast(self):
        self.merge(rows())
        self.assertEqual([0, 6, 12], self.merge(rows(leads=(0,))).TMD.tolist())

    def test_different_storm_or_cycle_cannot_read_backup(self):
        self.merge(rows())
        empty = rows().iloc[:0]
        self.assertTrue(self.merge(empty, replace(self.settings, typ_number=58)).empty)
        self.assertTrue(self.merge(empty, replace(self.settings, data_time="202610141200")).empty)

    def test_wrong_cycle_and_valid_time_rows_are_not_saved(self):
        wrong_time = rows()
        wrong_time.loc[wrong_time.TMD.gt(0), "FT_TM(UTC)"] = "202610151200"
        self.merge(pd.concat([rows(cycle="202610141200"), wrong_time]))
        self.assertIsNone(backup.read_snapshot(self.settings.source_backup_dir, STORM, CYCLE))

    def test_official_analysis_is_never_backed_up_or_replayed(self):
        self.merge(pd.concat([rows(model="KMA", source="APIHUB"), rows()]))
        recovered = self.merge(rows().iloc[:0])
        self.assertNotIn("KMA", set(recovered.SRC))
        self.assertEqual({"GFS"}, set(recovered.SRC))

    def test_qc_is_reapplied_and_invalid_fresh_track_does_not_destroy_backup(self):
        self.merge(rows())
        invalid = rows(leads=(0, 24))
        self.assertEqual([0, 6, 12], self.merge(invalid).TMD.tolist())
        stored = backup.read_snapshot(self.settings.source_backup_dir, STORM, CYCLE)
        stored["rows"][1]["LON"] = -179
        backup.write_snapshot(self.settings.source_backup_dir, stored)
        self.assertTrue(self.merge(rows().iloc[:0]).empty)

    def test_linked_td_to_typ_keeps_backup_without_using_other_storm(self):
        self.merge(rows())
        promoted = replace(self.settings, storm_stage="TYP", typ_number=30, linked_td_number=57)
        recovered = self.merge(rows().iloc[:0], promoted)
        self.assertEqual({30}, set(recovered.TYP))
        self.assertIsNotNone(backup.read_snapshot(self.settings.source_backup_dir, "typ_2026_30", CYCLE))

    def test_linked_aliases_do_not_splice_previous_longer_tail(self):
        self.merge(rows(leads=(0, 6, 12, 18, 24)))
        promoted = replace(self.settings, storm_stage="TYP", typ_number=30, linked_td_number=57)
        self.merge(rows(leads=(0, 6, 12), latitude=17), promoted)
        recovered = self.merge(rows().iloc[:0], promoted)
        self.assertEqual([0, 6, 12], recovered.TMD.tolist())
        self.assertEqual(17, recovered.LAT.iloc[0])

    def test_disabled_skip_atcf_and_old_cycle_do_not_touch_backup(self):
        for settings in (replace(self.settings, source_backup_dir=None), replace(self.settings, skip_atcf=True),
                         replace(self.settings, data_time="202610010600")):
            self.merge(rows(), settings)
        self.assertFalse(list(self.settings.source_backup_dir.rglob("*.gz")))


class BackupLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "backup"
        self.cache = Path(self.temp.name) / "kma"

    def prune(self):
        with redirect_stdout(io.StringIO()):
            return backup.prune(self.root, self.cache, now=NOW)

    def cache_rows(self, endpoint, records):
        self.cache.mkdir(exist_ok=True)
        (self.cache / f"{endpoint}_2026.json").write_text(json.dumps({"rows": records}), encoding="utf-8")

    def test_missing_lists_or_disappearing_forecast_is_not_an_end_signal(self):
        backup.write_snapshot(self.root, payload())
        self.assertEqual(1, len(self.prune()["files"]))

    def test_officially_ended_td_is_removed(self):
        backup.write_snapshot(self.root, payload())
        self.cache_rows("td_lst", [{"YY": 2026, "TD": 57, "TYP": 0, "TM_ED": "202610141200"}])
        self.assertEqual({}, self.prune()["files"])
        self.assertFalse((self.root / STORM).exists())

    def test_typ_downgraded_to_active_td_is_not_removed(self):
        key = "typ_2026_29"
        backup.write_snapshot(self.root, payload(key))
        self.cache_rows("typ_lst", [{"YY": 2026, "SEQ": 29, "NOW": 2, "TM_ED": "202610141200"}])
        self.cache_rows("td_lst", [{"YY": 2026, "TD": 56, "TYP": 29, "TM_ST": "202610141200", "TM_ED": ""}])
        self.assertEqual(1, len(self.prune()["files"]))

    def test_promotion_is_not_end_but_final_typ_end_removes_both_keys(self):
        backup.write_snapshot(self.root, payload())
        backup.write_snapshot(self.root, payload("typ_2026_30", aliases=["typ_2026_30", STORM]))
        self.cache_rows("td_lst", [{"YY": 2026, "TD": 57, "TYP": 30, "TM_ED": "202610141200"}])
        self.assertEqual(2, len(self.prune()["files"]))
        self.cache_rows("typ_lst", [{"YY": 2026, "SEQ": 30, "NOW": 2, "TM_ED": "202610141200"}])
        self.assertEqual({}, self.prune()["files"])

    def test_age_is_measured_from_cycle_not_latest_upload(self):
        backup.write_snapshot(self.root, payload(cycle="202610120600"))
        backup.write_snapshot(self.root, payload())
        self.assertEqual([f"{STORM}/{CYCLE}.json.gz"], list(self.prune()["files"]))

    def test_storage_limit_discards_oldest_cycle_first(self):
        backup.write_snapshot(self.root, payload(cycle="202610140000"))
        backup.write_snapshot(self.root, payload())
        with patch.object(backup, "MAX_TOTAL_BYTES", backup.snapshot_path(self.root, STORM, CYCLE).stat().st_size):
            self.assertEqual([f"{STORM}/{CYCLE}.json.gz"], list(self.prune()["files"]))

    def test_roundtrip_artifact_and_empty_index_replace_previous_files(self):
        backup.write_snapshot(self.root, payload())
        self.prune()
        target = Path(self.temp.name) / "restored"
        backup.restore_archive(target, artifact_zip(self.root))
        self.assertIsNotNone(backup.read_snapshot(target, STORM, CYCLE))
        backup.snapshot_path(self.root, STORM, CYCLE).unlink()
        self.prune()
        backup.restore_archive(target, artifact_zip(self.root))
        self.assertFalse(list(target.rglob("*.gz")))

    def test_corrupt_snapshot_and_path_traversal_are_rejected(self):
        stream = io.BytesIO()
        data = gzip.compress(json.dumps(payload()).encode())
        name = "../escaped.json.gz"
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("index.json", json.dumps({"version": 1, "files": {name: hashlib.sha256(data).hexdigest()}}))
            archive.writestr(name, data)
        with self.assertRaises(ValueError):
            backup.restore_archive(self.root, stream.getvalue())
        backup.write_snapshot(self.root, payload())
        path = backup.snapshot_path(self.root, STORM, CYCLE)
        path.write_bytes(b"corrupt")
        self.assertIsNone(backup.read_snapshot(self.root, STORM, CYCLE))

    def test_artifact_can_contain_safe_directory_entries(self):
        backup.write_snapshot(self.root, payload())
        self.prune()
        stream = io.BytesIO(artifact_zip(self.root))
        with zipfile.ZipFile(stream, "a") as archive:
            archive.writestr(STORM + "/", b"")
        target = Path(self.temp.name) / "restored"
        backup.restore_archive(target, stream.getvalue())
        self.assertIsNotNone(backup.read_snapshot(target, STORM, CYCLE))

    def test_restore_failure_leaves_previous_local_files_untouched(self):
        backup.write_snapshot(self.root, payload())
        self.prune()
        stream = io.BytesIO(artifact_zip(self.root))
        target = Path(self.temp.name) / "restored"
        backup.write_snapshot(target, payload())
        original = backup.snapshot_path(target, STORM, CYCLE).read_bytes()
        with zipfile.ZipFile(stream, "a") as archive:
            archive.writestr("unexpected.txt", b"not indexed")
        with self.assertRaises(ValueError):
            backup.restore_archive(target, stream.getvalue())
        self.assertEqual(original, backup.snapshot_path(target, STORM, CYCLE).read_bytes())

    def test_cleanup_does_not_delete_anything_when_new_artifact_is_wrong(self):
        current = {"name": "polarwx-requests", "workflow_run": {"id": 100}}
        with patch.object(backup, "github_request", return_value=current) as request:
            with self.assertRaises(ValueError):
                backup.cleanup(2)
        self.assertEqual(1, request.call_count)

    def test_corrupt_latest_artifact_falls_back_without_deleting_remote_backup(self):
        backup.write_snapshot(self.root, payload())
        self.prune()
        data = artifact_zip(self.root)
        artifacts = [{"id": 2, "expired": False}, {"id": 1, "expired": False}]
        with patch.object(backup, "list_artifacts", return_value=artifacts), \
                patch.object(backup, "github_request", side_effect=[b"corrupt", data]) as request, redirect_stdout(io.StringIO()):
            backup.restore(Path(self.temp.name) / "restored")
        self.assertEqual(2, request.call_count)
        self.assertTrue(all("method" not in call.kwargs for call in request.call_args_list))

    def test_cleanup_only_deletes_our_older_artifacts_after_upload(self):
        artifacts = [{"id": 3}, {"id": 2}, {"id": 1}]
        current = {"name": backup.ARTIFACT_NAME, "workflow_run": {"id": 100}}
        with patch.dict("os.environ", {"GITHUB_RUN_ID": "100"}), \
                patch.object(backup, "list_artifacts", return_value=artifacts), \
                patch.object(backup, "github_request", return_value=current) as request, redirect_stdout(io.StringIO()):
            backup.cleanup(2)
        self.assertEqual([(("/2",), {}), (("/1",), {"method": "DELETE"})], [(call.args, call.kwargs) for call in request.call_args_list])

    def test_redirect_does_not_leak_github_token(self):
        request = urllib.request.Request("https://api.github.com/backup", headers={"Authorization": "Bearer PRIVATE"})
        redirected = backup.SafeRedirect().redirect_request(request, None, 302, "Found", {}, "https://storage.example/backup")
        self.assertIsNone(redirected.get_header("Authorization"))


if __name__ == "__main__":
    unittest.main()
