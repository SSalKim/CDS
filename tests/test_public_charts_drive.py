import copy
import hashlib
import json
import os
import tempfile
import traceback
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import urlsplit

import public_charts_drive as charts


EMAIL = "charts@example.invalid"
FOLDER = "charts_folder"
KEY = "aifs/2026111500/024/gph500/asia"
ENV = {
    "PUBLIC_CHARTS_DRIVE_CLIENT_ID": "dedicated-client",
    "PUBLIC_CHARTS_DRIVE_CLIENT_SECRET": "private-client-secret",
    "PUBLIC_CHARTS_DRIVE_REFRESH_TOKEN": "private-refresh-token",
    "PUBLIC_CHARTS_DRIVE_FOLDER_ID": FOLDER,
    "PUBLIC_CHARTS_DRIVE_ACCOUNT_EMAIL": EMAIL,
}


class Response:
    def __init__(self, payload=None, *, content=None, headers=None, status=200):
        self.payload = copy.deepcopy(payload)
        self.content = content if content is not None else json.dumps(payload).encode()
        self.headers = headers or {}
        self.status_code = status

    def json(self):
        return copy.deepcopy(self.payload)


class FakeDriveClient:
    """An in-memory HTTP boundary; never opens an HTTP session or socket."""

    def __init__(self):
        self.email = EMAIL
        self.root_id = "my_drive_root_id"
        self.files = {}
        self.contents = {}
        self.permissions = {}
        self.versions = {}
        self.pending = None
        self.list_pages = None
        self.permission_pages = None
        self.corrupt_upload = False
        self.wrong_upload_size = False
        self.ignore_permission_write = False
        self.upload_location = charts.DRIVE_UPLOAD_API + "/files?upload_id=private-session"
        self.fail_patch = False
        self.metadata_overrides = {}
        self.omit_v3_etag = False
        self.v2_metadata_overrides = {}
        self.add(FOLDER, b"", mime=charts.FOLDER_MIME, tagged=False, parents=[self.root_id])
        self.request = Mock(side_effect=self.dispatch)

    def add(self, file_id, content=b"chart", *, mime="image/webp", tagged=True,
            key=KEY, parents=None, name=None, **overrides):
        item = {
            "id": file_id, "name": name or file_id, "mimeType": mime,
            "parents": [FOLDER] if parents is None else parents,
            "trashed": False, "ownedByMe": True, "owners": [{"emailAddress": EMAIL}],
            "size": str(len(content)), "md5Checksum": hashlib.md5(content).hexdigest(),
            "appProperties": ({"namespace": charts.NAMESPACE, "key": key,
                               "kind": "json" if mime == "application/json" else "image"}
                              if tagged else {}),
        }
        item.update(overrides)
        self.files[file_id] = item
        self.contents[file_id] = content
        self.permissions[file_id] = []
        self.versions[file_id] = '"version-1"'
        return item

    def store_content(self, file_id, content):
        self.contents[file_id] = content
        self.files[file_id]["size"] = str(len(content))
        self.files[file_id]["md5Checksum"] = hashlib.md5(content).hexdigest()
        self.versions[file_id] = '"version-2"'
        if self.corrupt_upload:
            self.files[file_id]["md5Checksum"] = "0" * 32
        if self.wrong_upload_size:
            self.files[file_id]["size"] = str(len(content) + 1)

    def dispatch(self, method, url, **kwargs):
        if kwargs.get("allow_redirects") is not False:
            raise AssertionError("All requests must refuse redirects")
        parsed = urlsplit(url)
        params = kwargs.get("params", {})
        if url == charts.DRIVE_API + "/about":
            return Response({"user": {"emailAddress": self.email}})
        if url == charts.DRIVE_API + "/files/root":
            return Response({"id": self.root_id})
        if url == charts.DRIVE_API + "/files":
            if self.list_pages is not None:
                return Response(self.list_pages.pop(0))
            # Deliberately include out-of-scope entries to test client-side guards.
            return Response({"files": list(self.files.values())})
        if parsed.path.endswith("/permissions"):
            file_id = parsed.path.split("/")[-2]
            if method == "POST":
                if not self.ignore_permission_write:
                    self.permissions[file_id].append({"id": "public", **kwargs["json"]})
                return Response({"id": "public"})
            if self.permission_pages is not None:
                return Response(self.permission_pages.pop(0))
            return Response({"permissions": self.permissions[file_id]})
        if method == "POST" and params.get("uploadType") == "resumable":
            self.pending = copy.deepcopy(kwargs["json"])
            return Response(headers={"Location": self.upload_location})
        if method == "PUT" and url == self.upload_location:
            file_id = "uploaded_" + str(len(self.files))
            content = kwargs["data"].read()
            metadata = self.pending
            self.add(file_id, content, mime=metadata["mimeType"], name=metadata["name"],
                     parents=metadata["parents"], appProperties=metadata["appProperties"])
            self.store_content(file_id, content)
            return Response({"id": file_id})
        file_id = parsed.path.split("/")[-1]
        if params.get("uploadType") == "multipart":
            if method in ("PATCH", "PUT"):
                if self.fail_patch or kwargs["headers"].get("If-Match") != self.versions[file_id]:
                    raise RuntimeError("HTTP 412 private-refresh-token")
            message = BytesParser(policy=policy.default).parsebytes(
                ("Content-Type: " + kwargs["headers"]["Content-Type"] + "\r\n\r\n").encode()
                + kwargs["data"]
            )
            parts = list(message.iter_parts())
            metadata = json.loads(parts[0].get_payload(decode=True))
            content = parts[1].get_payload(decode=True)
            if method == "POST":
                file_id = "json_" + str(len(self.files))
                self.add(file_id, content, mime=metadata["mimeType"], name=metadata["name"],
                         key=metadata["name"], appProperties=metadata["appProperties"],
                         parents=metadata["parents"])
            self.store_content(file_id, content)
            return Response({"id": file_id})
        if file_id not in self.files:
            raise RuntimeError("Missing ID private-refresh-token")
        if method == "DELETE":
            if kwargs["headers"].get("If-Match") != self.versions[file_id]:
                raise RuntimeError("HTTP 412")
            del self.files[file_id]
            return Response(status=204)
        if params.get("alt") == "media":
            return Response(content=self.contents[file_id])
        if parsed.path.startswith("/drive/v2/files/"):
            item = self.files[file_id]
            value = {"id": file_id, "title": item["name"], "mimeType": item["mimeType"],
                     "fileSize": item["size"], "md5Checksum": item["md5Checksum"],
                     "parents": [{"id": parent} for parent in item["parents"]],
                     "properties": [{"key": key, "value": value, "visibility": "PRIVATE"}
                                    for key, value in item["appProperties"].items()],
                     "labels": {"trashed": item["trashed"]}, "ownedByMe": item["ownedByMe"],
                     "owners": item["owners"], "driveId": item.get("driveId"),
                     "etag": self.versions.get(file_id)}
            return Response(self.v2_metadata_overrides.get(file_id, value))
        return Response(self.metadata_overrides.get(file_id, self.files[file_id]),
                        headers={} if self.omit_v3_etag else {"ETag": self.versions.get(file_id)})


class PublicChartDriveTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeDriveClient()
        self.store = charts.ChartDriveStore(self.client, FOLDER, EMAIL)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "chart.webp"
        self.path.write_bytes(b"chart-content")

    def methods(self, method):
        return [call for call in self.client.request.call_args_list if call.args[0] == method]

    def test_environment_uses_only_explicit_dedicated_oauth_configuration(self):
        with patch.dict(os.environ, {**ENV, "GOOGLE_DRIVE_REFRESH_TOKEN": "vtg-token"}, clear=True), \
                patch.object(charts, "DriveClient", return_value=self.client) as factory:
            result = charts.ChartDriveStore.from_environment()
        factory.assert_called_once_with({"mode": "oauth_refresh_token",
                                        "client_id": ENV["PUBLIC_CHARTS_DRIVE_CLIENT_ID"],
                                        "client_secret": ENV["PUBLIC_CHARTS_DRIVE_CLIENT_SECRET"],
                                        "refresh_token": ENV["PUBLIC_CHARTS_DRIVE_REFRESH_TOKEN"]})
        self.assertEqual(FOLDER, result.folder_id)
        self.assertTrue(result._verified)

    def test_generic_or_vtg_environment_never_authenticates(self):
        generic = {"GOOGLE_DRIVE_CLIENT_ID": "vtg-id", "GOOGLE_DRIVE_CLIENT_SECRET": "vtg-secret",
                   "GOOGLE_DRIVE_REFRESH_TOKEN": "vtg-token",
                   "VTG_ARCHIVE_DRIVE_FOLDER_ID": FOLDER,
                   "GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON": "vtg-service-account"}
        for settings in (generic, {**generic, **{k: v for k, v in ENV.items()
                                               if k != "PUBLIC_CHARTS_DRIVE_REFRESH_TOKEN"}}):
            with self.subTest(settings=list(settings)), patch.dict(os.environ, settings, clear=True), \
                    patch.object(charts, "DriveClient") as factory:
                with self.assertRaises(charts.ChartDriveError):
                    charts.ChartDriveStore.from_environment()
                factory.assert_not_called()

    def test_each_dedicated_setting_is_required(self):
        for missing in ENV:
            with self.subTest(missing=missing), patch.dict(
                os.environ, {k: v for k, v in ENV.items() if k != missing}, clear=True
            ), patch.object(charts, "DriveClient") as factory:
                with self.assertRaisesRegex(charts.ChartDriveError, missing):
                    charts.ChartDriveStore.from_environment()
                factory.assert_not_called()

    def test_auth_errors_and_system_exit_are_sanitized(self):
        for error in (RuntimeError("private-refresh-token"), SystemExit("private-client-secret")):
            with self.subTest(error=type(error)), patch.dict(os.environ, ENV, clear=True), \
                    patch.object(charts, "DriveClient", side_effect=error):
                with self.assertRaises(charts.ChartDriveError) as caught:
                    charts.ChartDriveStore.from_environment()
                rendered = "".join(traceback.format_exception(caught.exception))
                self.assertNotIn("private-refresh-token", rendered)
                self.assertNotIn("private-client-secret", rendered)

    def test_wrong_account_fails_before_folder_or_inventory_access(self):
        self.client.email = "vtg@example.invalid"
        with self.assertRaisesRegex(charts.ChartDriveError, "account does not match"):
            self.store.inventory()
        self.assertEqual(1, self.client.request.call_count)
        self.assertFalse(self.store._verified)

    def test_environment_rejects_wrong_account_and_invalid_targets(self):
        self.client.email = "vtg@example.invalid"
        with patch.dict(os.environ, ENV, clear=True), \
                patch.object(charts, "DriveClient", return_value=self.client):
            with self.assertRaisesRegex(charts.ChartDriveError, "account does not match"):
                charts.ChartDriveStore.from_environment()
        for changes in ({"PUBLIC_CHARTS_DRIVE_FOLDER_ID": "root"},
                        {"PUBLIC_CHARTS_DRIVE_ACCOUNT_EMAIL": "invalid"}):
            with self.subTest(changes=changes), patch.dict(os.environ, {**ENV, **changes}, clear=True), \
                    patch.object(charts, "DriveClient") as factory:
                with self.assertRaises(charts.ChartDriveError):
                    charts.ChartDriveStore.from_environment()
                factory.assert_not_called()

    def test_account_email_comparison_is_case_insensitive(self):
        self.client.email = EMAIL.upper()
        self.client.files[FOLDER]["owners"][0]["emailAddress"] = EMAIL.upper()
        self.assertEqual(EMAIL, self.store.verify_account_and_folder()["account_email"])

    def test_root_alias_and_actual_root_id_are_forbidden(self):
        for folder in ("root", "ROOT", "../root", "https://example.invalid/folder"):
            with self.subTest(folder=folder), self.assertRaises(charts.ChartDriveError):
                charts.ChartDriveStore(self.client, folder, EMAIL)
        self.store.folder_id = self.client.root_id
        with self.assertRaisesRegex(charts.ChartDriveError, "root"):
            self.store.verify_account_and_folder()
        self.assertFalse(self.methods("POST"))

    def test_invalid_folder_rejected_without_writes(self):
        for changes in ({"mimeType": "image/png"}, {"trashed": True}, {"trashed": None},
                        {"ownedByMe": False}, {"owners": [{"emailAddress": "vtg@example.invalid"}]},
                        {"owners": []}, {"driveId": "shared_drive"}, {"id": "another_folder"}):
            with self.subTest(changes=changes):
                original = copy.deepcopy(self.client.files[FOLDER])
                self.client.files[FOLDER].update(changes)
                with self.assertRaises(charts.ChartDriveError):
                    self.store.verify_account_and_folder()
                self.client.files[FOLDER] = original
        self.assertFalse(self.methods("POST"))

    def test_import_and_injected_construction_do_not_make_requests(self):
        self.assertEqual(0, self.client.request.call_count)

    def test_inventory_requires_both_parent_and_namespace(self):
        self.client.add("ours")
        self.client.add("untagged", tagged=False)
        self.client.add("vtg", appProperties={"vtg_path": "data/example.png"})
        self.client.add("wrong_namespace", appProperties={"namespace": "vtg"})
        self.client.add("nested", parents=["child_folder"])
        self.client.add("outside", parents=["another_folder"])
        self.client.add("shared", driveId="shared_drive")
        self.client.add("trashed", trashed=True)
        self.client.add("folder", mime=charts.FOLDER_MIME)
        self.assertEqual(["ours"], [item["id"] for item in self.store.inventory()])
        query = self.client.request.call_args.kwargs["params"]["q"]
        self.assertIn(f"'{FOLDER}' in parents", query)
        self.assertIn("key='namespace'", query)
        self.assertIn(charts.NAMESPACE, query)
        self.assertIn("trashed = false", query)

    def test_inventory_paginates_and_rejects_incomplete_or_looped_results(self):
        first = self.client.add("first")
        second = self.client.add("second")
        self.client.list_pages = [{"files": [first], "nextPageToken": "next"}, {"files": [second]}]
        self.assertEqual(["first", "second"], [item["id"] for item in self.store.inventory()])
        self.assertEqual("next", self.client.request.call_args.kwargs["params"]["pageToken"])
        for pages in ([{"files": [], "incompleteSearch": True}],
                      [{"files": [], "nextPageToken": "loop"}] * 2,
                      [{"files": "invalid"}]):
            self.client.list_pages = list(pages)
            with self.subTest(pages=pages), self.assertRaises(charts.ChartDriveError):
                self.store.inventory()

    def test_upload_verifies_integrity_and_public_permission(self):
        result = self.store.upload_image(self.path, KEY)
        content = self.path.read_bytes()
        self.assertEqual({"file_id", "url", "size", "md5", "sha256", "key"}, set(result))
        self.assertEqual(hashlib.md5(content).hexdigest(), result["md5"])
        self.assertEqual(hashlib.sha256(content).hexdigest(), result["sha256"])
        self.assertEqual(len(content), result["size"])
        self.assertEqual(KEY, result["key"])
        self.assertIn(result["file_id"], result["url"])
        metadata = self.client.files[result["file_id"]]
        self.assertEqual([FOLDER], metadata["parents"])
        self.assertEqual(charts.NAMESPACE, metadata["appProperties"]["namespace"])
        self.assertEqual(KEY, metadata["appProperties"]["key"])
        self.assertEqual("reader", self.client.permissions[result["file_id"]][0]["role"])

    def test_same_content_is_stable_and_changed_content_creates_immutable_file(self):
        first = self.store.upload_image(self.path, KEY)
        before = len(self.methods("PUT"))
        self.assertEqual(first, self.store.upload_image(self.path, KEY))
        self.assertEqual(before, len(self.methods("PUT")))
        self.path.write_bytes(b"different-chart")
        second = self.store.upload_image(self.path, KEY)
        self.assertNotEqual(first["file_id"], second["file_id"])
        self.assertEqual(b"chart-content", self.client.contents[first["file_id"]])
        self.assertFalse(self.methods("PATCH"))
        self.assertFalse(self.methods("DELETE"))

    def test_same_content_outside_folder_or_without_namespace_is_not_reused(self):
        content = self.path.read_bytes()
        for file_id, changes in (("outside", {"parents": ["foreign"]}),
                                 ("untagged", {"tagged": False}),
                                 ("wrongkey", {"key": "gfs/2026111500/024/gph500/asia"})):
            self.client.add(file_id, content, **changes)
        result = self.store.upload_image(self.path, KEY)
        self.assertTrue(result["file_id"].startswith("uploaded_"))

    def test_cached_candidate_is_refetched_before_reuse_or_publication(self):
        self.client.add("moved", self.path.read_bytes())
        moved = copy.deepcopy(self.client.files["moved"])
        moved["parents"] = ["foreign"]
        self.client.metadata_overrides["moved"] = moved
        with self.assertRaises(charts.ChartDriveError):
            self.store.upload_image(self.path, KEY)
        self.assertFalse(self.methods("POST"))

    def test_size_or_md5_must_both_match_for_reuse(self):
        existing = self.client.add("old", self.path.read_bytes())
        existing["size"] = "999"
        result = self.store.upload_image(self.path, KEY)
        self.assertNotEqual("old", result["file_id"])

    def test_existing_wrong_md5_with_correct_size_is_not_reused(self):
        existing = self.client.add("old", self.path.read_bytes())
        existing["md5Checksum"] = "0" * 32
        self.assertNotEqual("old", self.store.upload_image(self.path, KEY)["file_id"])

    def test_upload_integrity_mismatch_never_publishes_or_deletes(self):
        self.client.corrupt_upload = True
        with self.assertRaisesRegex(charts.ChartDriveError, "integrity"):
            self.store.upload_image(self.path, KEY)
        public_calls = [call for call in self.methods("POST") if "/permissions" in call.args[1]]
        self.assertFalse(public_calls)
        self.assertFalse(self.methods("DELETE"))

    def test_upload_size_mismatch_never_publishes(self):
        self.client.wrong_upload_size = True
        with self.assertRaisesRegex(charts.ChartDriveError, "integrity"):
            self.store.upload_image(self.path, KEY)
        self.assertFalse([call for call in self.methods("POST") if "/permissions" in call.args[1]])

    def test_all_four_models_use_the_same_key_contract(self):
        for model in ("aifs", "gfs", "aigfs", "cmc"):
            key = f"{model}/2026111500/240/wnd925/hkor"
            with self.subTest(model=model):
                self.assertEqual(key, self.store.upload_image(self.path, key)["key"])

    def test_zero_hour_instantaneous_fields_preserve_keys_and_image_metadata(self):
        for model in ("aifs", "gfs", "aigfs", "cmc"):
            for domain in ("asia", "hkor"):
                key = f"{model}/2026111500/000/gph500/{domain}"
                with self.subTest(model=model, domain=domain):
                    result = self.store.upload_image(self.path, key)
                    self.assertEqual(key, result["key"])
                    self.assertEqual(result, self.store.upload_image(self.path, key))
        inventory = self.store.inventory()
        self.assertEqual(8, len(inventory))
        for metadata in inventory:
            self.assertEqual("image", metadata["appProperties"]["kind"])
            self.assertIn("/000/", metadata["appProperties"]["key"])

    def test_legacy_korea_domain_is_rejected_without_normalization_or_network(self):
        for hour in ("000", "024", "240"):
            key = f"aifs/2026111500/{hour}/gph500/korea"
            with self.subTest(hour=hour), self.assertRaises(charts.ChartDriveError):
                self.store.upload_image(self.path, key)
        self.assertEqual(0, self.client.request.call_count)

    def test_permission_creation_must_be_verified(self):
        self.client.ignore_permission_write = True
        with self.assertRaisesRegex(charts.ChartDriveError, "public reader verification"):
            self.store.upload_image(self.path, KEY)

    def test_existing_public_reader_is_reused_but_public_writer_is_rejected(self):
        self.client.add("existing", self.path.read_bytes())
        self.client.permissions["existing"] = [{"type": "anyone", "role": "reader"}]
        self.assertEqual("existing", self.store.upload_image(self.path, KEY)["file_id"])
        self.assertFalse(self.methods("POST"))
        self.client.permissions["existing"][0]["role"] = "writer"
        with self.assertRaisesRegex(charts.ChartDriveError, "permission role"):
            self.store.upload_image(self.path, KEY)

    def test_permissions_are_paginated(self):
        self.client.add("existing", self.path.read_bytes())
        self.client.permission_pages = [{"permissions": [], "nextPageToken": "next"},
                                        {"permissions": [{"type": "anyone", "role": "reader"}]}]
        self.assertEqual("existing", self.store.upload_image(self.path, KEY)["file_id"])
        self.assertFalse(self.methods("POST"))

    def test_untrusted_upload_destination_is_rejected_before_sending_bytes(self):
        for url in ("https://example.invalid/upload", "http://www.googleapis.com/upload/drive/v3/files",
                    "https://www.googleapis.com@evil.invalid/upload/drive/v3/files",
                    "https://www.googleapis.com:444/upload/drive/v3/files", ""):
            self.client.upload_location = url
            with self.subTest(url=url), self.assertRaises(charts.ChartDriveError):
                self.store.upload_image(self.path, KEY)
        self.assertFalse(self.methods("PUT"))

    def test_invalid_keys_paths_empty_images_and_json_names_fail_before_network(self):
        for key in ("../state.json", "aifs/2026023000/024/gph500/asia",
                    "aifs/2026111500/999/gph500/asia", KEY + "'", None):
            with self.subTest(key=key), self.assertRaises(charts.ChartDriveError):
                self.store.upload_image(self.path, key)
        self.path.write_bytes(b"")
        with self.assertRaises(charts.ChartDriveError):
            self.store.upload_image(self.path, KEY)
        with self.assertRaises(charts.ChartDriveError):
            self.store.upload_image(self.path.with_name("missing.webp"), KEY)
        for name in ("../state.json", "other.json", "STATE.JSON", None):
            with self.subTest(name=name), self.assertRaises(charts.ChartDriveError):
                self.store.write_json(name, {})
            with self.subTest(name=name), self.assertRaises(charts.ChartDriveError):
                self.store.read_json(name, {})
        self.assertEqual(0, self.client.request.call_count)

    def test_json_create_read_and_conditional_update_preserve_managed_id(self):
        for name in ("state.json", "manifest.json"):
            with self.subTest(name=name):
                default = {"missing": True}
                self.assertIs(default, self.store.read_json(name, default))
                first = self.store.write_json(name, {"cycles": ["2026111500"]})
                self.assertEqual({"cycles": ["2026111500"]}, self.store.read_json(name, default))
                second = self.store.write_json(name, {"cycles": ["2026111512"]})
                self.assertEqual(first["file_id"], second["file_id"])
                self.assertEqual({"cycles": ["2026111512"]}, self.store.read_json(name, default))
                self.assertTrue(self.methods("PATCH")[-1].kwargs["headers"]["If-Match"])
                self.assertFalse(self.client.permissions[first["file_id"]])

    def test_identical_json_is_not_rewritten(self):
        first = self.store.write_json("state.json", {"b": 2, "a": 1})
        self.assertEqual(first, self.store.write_json("state.json", {"a": 1, "b": 2}))
        self.assertFalse(self.methods("PATCH"))

    def test_json_does_not_overwrite_untagged_same_name(self):
        original = self.client.add("foreign", b"private", name="state.json",
                                   mime="application/json", tagged=False)
        result = self.store.write_json("state.json", {})
        self.assertNotEqual("foreign", result["file_id"])
        self.assertEqual(original, self.client.files["foreign"])
        self.assertEqual(b"private", self.client.contents["foreign"])

    def test_json_unicode_and_top_level_values_round_trip(self):
        for payload in ({"label": "\ud55c\ubc18\ub3c4"}, [1, 2], None):
            with self.subTest(payload=payload):
                self.store.write_json("state.json", payload)
                self.assertEqual(payload, self.store.read_json("state.json", "absent"))

    def test_json_upload_integrity_failure_is_not_silently_accepted(self):
        self.client.corrupt_upload = True
        with self.assertRaisesRegex(charts.ChartDriveError, "integrity"):
            self.store.write_json("state.json", {"value": True})

    def test_json_duplicate_or_invalid_managed_entry_fails_closed(self):
        self.client.add("state1", b"{}", name="state.json", key="state.json", mime="application/json")
        self.client.add("state2", b"{}", name="state.json", key="state.json", mime="application/json")
        with self.assertRaisesRegex(charts.ChartDriveError, "Duplicate"):
            self.store.write_json("state.json", {})
        del self.client.files["state2"]
        self.client.files["state1"]["appProperties"]["key"] = KEY
        with self.assertRaisesRegex(charts.ChartDriveError, "metadata"):
            self.store.read_json("state.json", {})

    def test_json_update_requires_etag_and_rejects_concurrent_changes(self):
        first = self.store.write_json("state.json", {"old": True})
        self.client.versions[first["file_id"]] = None
        with self.assertRaisesRegex(charts.ChartDriveError, "ETag"):
            self.store.write_json("state.json", {"new": True})
        self.client.versions[first["file_id"]] = '"changed"'
        self.client.fail_patch = True
        with self.assertRaises(charts.ChartDriveError):
            self.store.write_json("state.json", {"new": True})
        self.assertEqual({"old": True}, self.store.read_json("state.json"))

    def test_json_integrity_and_syntax_errors_never_return_default(self):
        first = self.store.write_json("manifest.json", {})
        self.client.contents[first["file_id"]] = b"different"
        with self.assertRaisesRegex(charts.ChartDriveError, "integrity"):
            self.store.read_json("manifest.json", {"fallback": True})
        self.client.store_content(first["file_id"], b"not-json")
        with self.assertRaisesRegex(charts.ChartDriveError, "invalid"):
            self.store.read_json("manifest.json", {})

    def test_json_updates_use_conditional_v2_when_v3_omits_etag(self):
        self.client.omit_v3_etag = True
        self.store.write_json("state.json", {"old": True})
        self.store.write_json("state.json", {"new": True})
        self.assertEqual({"new": True}, self.store.read_json("state.json"))
        update = self.methods("PUT")[-1]
        self.assertTrue(update.args[1].startswith(charts.DRIVE_V2_UPLOAD_API))
        self.assertTrue(update.kwargs["headers"]["If-Match"])
        self.assertEqual("false", update.kwargs["params"]["newRevision"])
        self.client.fail_patch = True
        with self.assertRaises(charts.ChartDriveError):
            self.store.write_json("state.json", {"stale": True})

    def test_v2_snapshot_rechecks_ownership_and_parent_before_mutation(self):
        first = self.store.write_json("state.json", {"old": True})
        self.client.omit_v3_etag = True
        self.client.v2_metadata_overrides[first["file_id"]] = {"id": first["file_id"],
                                                              "parents": [{"id": "outside"}]}
        with self.assertRaises(charts.ChartDriveError):
            self.store.write_json("state.json", {"new": True})
        self.assertFalse(self.methods("PUT"))

    def test_v2_delete_keeps_etag_guard_when_v3_omits_it(self):
        self.client.add("remove")
        self.client.omit_v3_etag = True
        self.store.delete_managed("remove")
        call = self.methods("DELETE")[-1]
        self.assertEqual(charts.DRIVE_V2_API + "/files/remove", call.args[1])
        self.assertEqual('"version-1"', call.kwargs["headers"]["If-Match"])

    def test_v2_delete_rejects_a_move_after_the_guarded_snapshot(self):
        self.client.add("moving_v2")
        self.client.omit_v3_etag = True
        dispatch = self.client.dispatch

        def move_before_delete(method, url, **kwargs):
            if method == "DELETE":
                self.client.files["moving_v2"]["parents"] = ["outside"]
                self.client.versions["moving_v2"] = '"moved-version"'
            return dispatch(method, url, **kwargs)

        self.client.request.side_effect = move_before_delete
        with self.assertRaises(charts.ChartDriveError):
            self.store.delete_managed("moving_v2")
        self.assertIn("moving_v2", self.client.files)

    def test_json_refetch_rejects_moved_or_untagged_entries(self):
        first = self.store.write_json("state.json", {})
        self.client.metadata_overrides[first["file_id"]] = {
            **self.client.files[first["file_id"]], "parents": ["outside"],
        }
        with self.assertRaises(charts.ChartDriveError):
            self.store.write_json("state.json", {"new": True})
        with self.assertRaises(charts.ChartDriveError):
            self.store.read_json("state.json", {})
        self.assertFalse(self.methods("PATCH"))

    def test_invalid_json_payload_never_contacts_drive(self):
        for value in ({"number": float("nan")}, {"set": {1, 2}}):
            with self.subTest(value=value), self.assertRaises(charts.ChartDriveError):
                self.store.write_json("state.json", value)
        self.assertEqual(0, self.client.request.call_count)

    def test_delete_refetches_and_permanently_deletes_only_requested_id(self):
        self.client.add("remove")
        self.client.add("keep")
        self.store.delete_managed("remove")
        self.assertNotIn("remove", self.client.files)
        self.assertIn("keep", self.client.files)
        call = self.methods("DELETE")[0]
        self.assertEqual(charts.DRIVE_API + "/files/remove", call.args[1])
        self.assertEqual('"version-1"', call.kwargs["headers"]["If-Match"])
        self.assertFalse(self.methods("PATCH"))

    def test_delete_rejects_outside_untagged_folders_shortcuts_and_foreign_owners(self):
        changes_list = [dict(parents=["outside"]), dict(parents=["child_folder"]),
                        dict(appProperties={}), dict(appProperties={"namespace": "vtg"}),
                        dict(ownedByMe=False), dict(owners=[{"emailAddress": "vtg@example.invalid"}]),
                        dict(mimeType=charts.FOLDER_MIME), dict(trashed=True),
                        dict(mimeType=None),
                        dict(mimeType="application/vnd.google-apps.shortcut")]
        for index, changes in enumerate(changes_list):
            file_id = "unsafe_" + str(index)
            self.client.add(file_id, **changes)
            with self.subTest(changes=changes), self.assertRaises(charts.ChartDriveError):
                self.store.delete_managed(file_id)
        for file_id in (FOLDER, "root", "../foreign"):
            with self.subTest(file_id=file_id), self.assertRaises(charts.ChartDriveError):
                self.store.delete_managed(file_id)
        self.assertFalse(self.methods("DELETE"))

    def test_delete_does_not_trust_prior_inventory(self):
        self.client.add("moved")
        self.assertEqual("moved", self.store.inventory()[0]["id"])
        self.client.files["moved"]["parents"] = ["outside"]
        with self.assertRaises(charts.ChartDriveError):
            self.store.delete_managed("moved")
        self.assertFalse(self.methods("DELETE"))

    def test_delete_requires_etag(self):
        self.client.add("remove")
        self.client.versions["remove"] = None
        with self.assertRaisesRegex(charts.ChartDriveError, "ETag"):
            self.store.delete_managed("remove")
        self.assertFalse(self.methods("DELETE"))

    def test_delete_concurrent_move_is_blocked_by_etag(self):
        self.client.add("moving")
        dispatch = self.client.dispatch

        def move_before_delete(method, url, **kwargs):
            if method == "DELETE":
                self.client.files["moving"]["parents"] = ["outside"]
                self.client.versions["moving"] = '"moved-version"'
            return dispatch(method, url, **kwargs)

        self.client.request.side_effect = move_before_delete
        with self.assertRaises(charts.ChartDriveError):
            self.store.delete_managed("moving")
        self.assertIn("moving", self.client.files)

    def test_api_errors_are_sanitized_and_never_become_empty_inventory(self):
        self.client.request.side_effect = RuntimeError("Bearer access-token private-refresh-token")
        with self.assertRaises(charts.ChartDriveError) as caught:
            self.store.inventory()
        rendered = "".join(traceback.format_exception(caught.exception))
        self.assertNotIn("access-token", rendered)
        self.assertNotIn("private-refresh-token", rendered)

    def test_redirect_and_invalid_metadata_are_rejected(self):
        for response in (Response(status=302), Response(["not an object"])):
            self.client.request.side_effect = None
            self.client.request.return_value = response
            with self.subTest(status=response.status_code), self.assertRaises(charts.ChartDriveError):
                self.store.verify_account_and_folder()


if __name__ == "__main__":
    unittest.main()
