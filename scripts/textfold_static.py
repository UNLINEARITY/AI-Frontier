"""Write TextFold's native browser reader as a GitHub Pages static document."""

from __future__ import annotations

import html
import gzip
import json
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


_ID = re.compile(r"^([a-z0-9][a-z0-9_-]*):([a-z0-9][a-z0-9_-]*)$")
_IMAGE_PATH = re.compile(r"(?<![/:])assets/textfold-images/")
_READER_KEYS = ("meta", "atoms", "units", "chunks", "blocks", "bib", "edges", "alias")


def _safe_record_id(record: dict[str, Any]) -> tuple[str, str]:
    match = _ID.fullmatch(str(record.get("id", "")))
    if not match:
        raise ValueError("record.id must be a vendor:slug pair of lowercase letters, digits, hyphens, or underscores")
    return match.group(1), match.group(2)


def _rebase_images(value: Any) -> Any:
    if isinstance(value, str):
        return _IMAGE_PATH.sub("../../assets/textfold-images/", value)
    if isinstance(value, list):
        return [_rebase_images(item) for item in value]
    if isinstance(value, dict):
        return {key: _rebase_images(item) for key, item in value.items()}
    return value


def copy_static_assets(root: Path, output: Path) -> None:
    """Copy the shared native reader, theme adapter and KaTeX assets into Pages output."""
    root = Path(root)
    output = Path(output)
    source = root / "site" / "vendor" / "textfold"
    target = output / "assets" / "textfold"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("reader.js", "reader.css", "i18n.js", "theme.js", "site-overrides.css", "inline.js", "inline.css", "inline.html", "LICENSE", "NOTICE"):
        shutil.copy2(source / name, target / name)
    shutil.copytree(source / "katex", target / "katex", dirs_exist_ok=True)


def write_static_reader(root: Path, output: Path, record: dict[str, Any], doc: dict[str, Any]) -> str:
    """Write one TextFold reader page and return its path relative to Pages output.

    ``output`` is the built site root. The native payload is embedded as safe JSON;
    referenced figure images remain separate static files under assets/.
    """
    root = Path(root)
    output = Path(output)
    vendor, slug = _safe_record_id(record)
    template = (root / "site" / "vendor" / "textfold" / "template.html").read_text(encoding="utf-8")
    if not isinstance(doc.get("meta"), dict):
        raise ValueError("TextFold document is missing meta")

    payload = {key: doc[key] for key in _READER_KEYS if key in doc}
    if not {"meta", "atoms", "units", "chunks", "blocks"}.issubset(payload):
        raise ValueError("TextFold document is missing a required reader field")
    meta = dict(payload["meta"])
    meta.update({
        "id": str(record["id"]),
        "title": str(record.get("title") or meta.get("title") or record["id"]),
        "label": "AI Frontier source",
        "abs_url": str(record.get("source_url") or meta.get("abs_url") or ""),
        "source": {"kind": "markdown", "name": "AI Frontier"},
        "local": True,
        "static": True,
        "ai_generated": False,
        "langs": [meta.get("lang", "en")],
    })
    payload["meta"] = meta
    payload["katex"] = "../../assets/textfold/katex/"
    payload = _rebase_images(payload)
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    title = html.escape(meta["title"], quote=True)
    data_name = f"{slug}.tfd"
    source_url = str(record.get("source_url") or meta.get("abs_url") or "")
    parts = urlsplit(source_url)
    if parts.scheme != "https" or not parts.netloc:
        source_url = ""
    page = (template.replace("{{TITLE}}", title).replace("{{DATA_URL}}", data_name)
            .replace("{{SOURCE_URL}}", html.escape(source_url, quote=True)))

    relative = f"fold/{vendor}/{slug}.html"
    destination = output / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")
    destination.with_name(data_name).write_bytes(gzip.compress(encoded.encode("utf-8"), mtime=0))
    return relative
