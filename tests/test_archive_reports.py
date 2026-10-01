"""Regression checks for preserving original bytes and previous snapshots."""

import importlib.util
import io
import json
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
                           document_type="technical_report",
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

    def test_retrieval_snapshot_uses_short_filename(self):
        self.source.pop("version")
        row = self.download(pdf())
        self.assertEqual(row["local_path"], "pdfs/openai/technical-reports/example.pdf")
        self.assertRegex(row["version"], r"^snapshot-\d{4}-\d{2}-\d{2}$")

    def test_short_filename_keeps_changed_and_repeated_refreshes(self):
        self.source.pop("version")
        first = self.download(pdf())
        previous = {("openai", self.source["pdf_url"]): first}
        second = self.download(pdf(200), previous, refresh=True)
        self.assertEqual(first["local_path"], "pdfs/openai/technical-reports/example.pdf")
        self.assertEqual(second["local_path"], f"pdfs/openai/technical-reports/example--{second['sha256'][:8]}.pdf")
        previous = {("openai", self.source["pdf_url"]): second}
        repeated = self.download(pdf(200), previous, refresh=True)
        self.assertEqual(repeated["local_path"], second["local_path"])
        self.assertEqual(len(list(self.root.rglob("*.pdf"))), 2)
        self.assertEqual((self.root / first["local_path"]).read_bytes(), pdf())
        self.assertEqual((self.root / second["local_path"]).read_bytes(), pdf(200))

    def test_explicit_revision_stays_in_filename(self):
        self.source["version"] = "arxiv-v2"
        row = self.download(pdf())
        self.assertEqual(row["local_path"], "pdfs/openai/technical-reports/example--arxiv-v2.pdf")

    def test_downloads_go_to_their_document_type_directory(self):
        self.source.pop("version")
        for kind, directory in [("technical_report", "technical-reports"),
                                ("model_card", "model-cards"), ("system_card", "system-cards")]:
            with self.subTest(document_type=kind):
                self.source["document_type"] = kind
                row = self.download(pdf())
                self.assertEqual(row["status"], "archived")
                self.assertEqual(row["local_path"], f"pdfs/openai/{directory}/example.pdf")
                self.assertTrue((self.root / row["local_path"]).is_file())

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

    def test_coverage_does_not_claim_failed_pdf_is_archived(self):
        (self.root / "sources.json").write_text(json.dumps([self.source]))
        model = dict(vendor="openai", model="Example model", status="archived",
                     source_url=self.source["pdf_url"], report_slugs=["example"],
                     note_en="Report date unknown.", note_cn="报告日期未确认。")
        (self.root / "model-coverage.json").write_text(json.dumps(
            dict(checked_at="2026-10-01", models=[model])))
        archive.render_model_coverage([])
        english = (self.root / "LATEST_MODELS.md").read_text()
        chinese = (self.root / "LATEST_MODELS_CN.md").read_text()
        self.assertIn("PDF not yet archived", english)
        self.assertNotIn("PDF archived", english)
        self.assertIn("PDF 待收录", chinese)
        self.assertIn("pdfs/openai/README_CN.md", chinese)
        row = dict(vendor="openai", title="Example", status="archived",
                   local_path="pdfs/openai/technical-reports/example.pdf",
                   source_updated_date="", retrieved_at="2026-10-01")
        archive.render_model_coverage([row])
        self.assertIn("[Example](pdfs/openai/technical-reports/example.pdf)",
                      (self.root / "LATEST_MODELS.md").read_text())


if __name__ == "__main__":
    unittest.main()
