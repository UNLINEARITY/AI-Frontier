"""Regression checks for preserving original bytes and previous snapshots."""

import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pypdf import PdfWriter

spec = importlib.util.spec_from_file_location(
    "archive_reports", Path(__file__).resolve().parents[1] / "scripts/archive_reports.py")
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


def pdf(width=100):
    writer = PdfWriter()
    writer.add_blank_page(width=width, height=100)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


class Response(io.BytesIO):
    headers = {}

    def geturl(self):
        return "https://example.org/report.pdf"


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.patcher = patch.object(archive, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.source = dict(vendor="openai", title="Example", slug="example",
                           pdf_url="https://example.org/report.pdf", version="snapshot-test")

    def download(self, data, previous=None, refresh=False):
        with patch.object(archive.urllib.request, "urlopen", return_value=Response(data)):
            return archive.fetch_one(self.source, previous or {}, refresh)

    def test_html_response_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not a PDF"):
            archive.inspect_pdf(b"<html>error page</html>")

    def test_oversized_response_is_not_saved(self):
        response = Response(b"")
        response.headers = {"Content-Length": str(archive.LIMIT + 1)}
        with patch.object(archive.urllib.request, "urlopen", return_value=response):
            row = archive.fetch_one(self.source, {}, False)
        self.assertEqual(row["status"], "oversized")
        self.assertFalse(list(self.root.rglob("*.pdf")))

    def test_changed_snapshot_preserves_both_files(self):
        first = self.download(pdf())
        previous = {("openai", self.source["pdf_url"]): first}
        second = self.download(pdf(200), previous, refresh=True)
        self.assertNotEqual(first["local_path"], second["local_path"])
        self.assertEqual((self.root / first["local_path"]).read_bytes(), pdf())
        self.assertEqual((self.root / second["local_path"]).read_bytes(), pdf(200))

    def test_failed_refresh_keeps_previous_archive(self):
        first = self.download(pdf())
        previous = {("openai", self.source["pdf_url"]): first}
        with patch.object(archive.urllib.request, "urlopen", side_effect=OSError("offline")), \
                patch.object(archive.time, "sleep"):
            row = archive.fetch_one(self.source, previous, True)
        self.assertEqual(row["status"], "archived")
        self.assertEqual(row["sha256"], first["sha256"])
        self.assertIn("Refresh failed", row["notes"])

    def test_corrupted_local_archive_is_detected(self):
        first = self.download(pdf())
        (self.root / first["local_path"]).write_bytes(pdf(200))
        previous = {("openai", self.source["pdf_url"]): first}
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            archive.fetch_one(self.source, previous, False)


if __name__ == "__main__":
    unittest.main()
