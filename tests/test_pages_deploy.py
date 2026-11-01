import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import pages_deploy as pages


class PagesDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.root.mkdir()
        self.git("init")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        for path in pages.REQUIRED_PATHS:
            self.write(path, "{}" if path.endswith(".json") else "test")
        self.write("pages_deploy.py", "packaging policy")
        self.write(".github/workflows/pages.yml", "deployment policy")
        self.write("VTG.py", "private operational code")
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", "-c", f"safe.directory={self.root.as_posix()}",
                                        *args], cwd=self.root, stderr=subprocess.DEVNULL).decode().strip()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "test")
        return self.git("rev-parse", "HEAD")

    def test_unchanged_public_tree_skips_operational_only_commit(self):
        previous = self.git("rev-parse", "HEAD")
        self.write("VTG.py", "updated collection logic")
        self.commit()
        report, _ = pages.plan(self.root, previous)
        self.assertFalse(report["needed"])
        self.assertTrue(pages.plan(self.root, previous, force=True)[0]["needed"])

    def test_each_public_or_packaging_change_requires_publication(self):
        for path in ("index.html", "data/status.json", "data/2026/image.png",
                     "pages_deploy.py", ".github/workflows/pages.yml"):
            previous = self.git("rev-parse", "HEAD")
            self.write(path, "changed " + path)
            self.commit()
            self.assertTrue(pages.plan(self.root, previous)[0]["needed"], path)

    def test_public_deletion_requires_publication(self):
        self.write("data/2026/old.png", "image")
        previous = self.commit()
        (self.root / "data/2026/old.png").unlink()
        self.commit()
        self.assertTrue(pages.plan(self.root, previous)[0]["needed"])

    def test_staging_preserves_bytes_and_excludes_untracked_and_hidden_files(self):
        self.write("data/2026/model.png", "image bytes")
        self.write("data/.secret", "secret")
        self.commit()
        self.write("untracked.js", "not deployed")
        self.write("data/untracked.json", "not deployed")
        report, public = pages.plan(self.root)
        destination = Path(self.temp.name) / "site"
        pages.prepare(self.root, destination, report, public)
        self.assertFalse((destination / "VTG.py").exists())
        self.assertFalse((destination / "pages_deploy.py").exists())
        self.assertFalse((destination / "untracked.js").exists())
        self.assertFalse((destination / "data/untracked.json").exists())
        self.assertFalse((destination / "data/.secret").exists())
        image = "data/2026/model.png"
        self.assertEqual(hashlib.sha256((self.root / image).read_bytes()).digest(),
                         hashlib.sha256((destination / image).read_bytes()).digest())
        self.assertEqual(report["commit"], json.loads((destination / "deployment.json").read_text())["commit"])

    def test_missing_entrypoints_and_unsafe_destinations_fail_closed(self):
        report, public = pages.plan(self.root)
        with self.assertRaisesRegex(ValueError, "outside"):
            pages.prepare(self.root, self.root / "site", report, public)
        (self.root / "radar.html").unlink()
        self.commit()
        with self.assertRaisesRegex(ValueError, "radar.html"):
            pages.plan(self.root)

    def test_sparse_plan_downloads_public_files_only_when_materialized(self):
        self.git("sparse-checkout", "set", "--no-cone", "/pages_deploy.py")
        self.assertFalse((self.root / "index.html").exists())
        report, public = pages.plan(self.root)
        destination = Path(self.temp.name) / "sparse-site"
        pages.prepare(self.root, destination, report, public, materialize=True)
        self.assertTrue((destination / "index.html").is_file())
        self.assertFalse((self.root / "VTG.py").exists())

    def test_comparison_never_requests_blob_sizes_in_a_partial_clone(self):
        original = pages.git
        calls = []

        def observed(root, *args, **kwargs):
            calls.append(args)
            return original(root, *args, **kwargs)

        with patch.object(pages, "git", side_effect=observed):
            pages.plan(self.root, self.git("rev-parse", "HEAD"))
        for args in calls:
            if args[0] == "ls-tree":
                self.assertNotIn("-l", args)


if __name__ == "__main__":
    unittest.main()
