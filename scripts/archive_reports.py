"""Download the curated official PDF list and maintain its verifiable index."""

import argparse
import csv
import hashlib
import io
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 100 * 1024 * 1024
VENDORS = {
    "openai": "OpenAI", "anthropic": "Anthropic", "google": "Google / DeepMind",
    "meta": "Meta", "xai": "xAI", "mistral": "Mistral AI", "nvidia": "NVIDIA",
    "deepseek": "DeepSeek", "qwen": "Alibaba / Qwen", "moonshot": "Moonshot AI / Kimi",
    "zai": "智谱 / Z.ai", "minimax": "MiniMax",
}
FIELDS = ["vendor", "title", "document_type", "published_date", "source_updated_date",
          "version", "source_url", "pdf_url", "resolved_url", "local_path", "retrieved_at",
          "sha256", "size_bytes", "pages", "status", "notes"]


def inspect_pdf(data):
    if not data.startswith(b"%PDF-"):
        raise ValueError("Response is not a PDF")
    if len(data) > LIMIT:
        raise ValueError("PDF exceeds GitHub's 100 MiB ordinary Git limit")
    reader = PdfReader(io.BytesIO(data), strict=False)
    pages = len(reader.pages)
    if not pages:
        raise ValueError("PDF has no pages")
    return hashlib.sha256(data).hexdigest(), pages


def read_catalog():
    path = ROOT / "catalog.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def fetch_one(source, previous, refresh):
    row = {key: str(source.get(key, "")) for key in FIELDS}
    row["status"] = "pending"
    old = previous.get((row["vendor"], row["pdf_url"]))
    if old and old["status"] == "archived" and not refresh:
        path = ROOT / old["local_path"]
        if path.is_file():
            digest, pages = inspect_pdf(path.read_bytes())
            if digest != old["sha256"]:
                raise ValueError(f"Local hash mismatch: {path}")
            return {**old, **{k: row[k] for k in ["title", "document_type", "published_date",
                    "source_updated_date", "source_url", "notes"]}, "pages": str(pages)}
    if not row["pdf_url"]:
        row["status"] = "missing_pdf"
        return row
    try:
        urls = [row["pdf_url"], *source.get("alternate_pdf_urls", [])]
        arxiv = re.fullmatch(r"https://arxiv.org/pdf/(\d{4}\.\d{4,5})(v\d+)", row["pdf_url"])
        if arxiv:
            urls += [f"https://arxiv.org/pdf/{arxiv[1]}", f"https://arxiv.org/pdf/{arxiv[1]}{arxiv[2]}.pdf",
                     f"https://arxiv.org/pdf/{arxiv[1]}.pdf", f"https://export.arxiv.org/pdf/{arxiv[1]}{arxiv[2]}"]
        last_error = None
        for attempt in range(max(3, len(urls))):
            try:
                url = urls[min(attempt, len(urls) - 1)]
                request = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (AI-Frontier-PDF-Archive/1.0)"})
                with urllib.request.urlopen(request, timeout=90) as response:
                    if int(response.headers.get("Content-Length", "0")) > LIMIT:
                        raise ValueError(f"PDF exceeds 100 MiB ({response.headers['Content-Length']} bytes); official link retained")
                    data = response.read(LIMIT + 1)
                    row["resolved_url"] = response.geturl()
                digest, pages = inspect_pdf(data)
                if arxiv and url != row["pdf_url"]:
                    # An unversioned endpoint must prove that it served the requested revision.
                    text = "".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages[:2])
                    if not re.search(re.escape(arxiv[1]) + re.escape(arxiv[2]) + r"\b", text):
                        raise ValueError("Alternate arXiv PDF does not prove the requested version")
                break
            except Exception as error:
                last_error = error
                if "exceeds" in str(error) and "MiB" in str(error):
                    raise
                if attempt == max(3, len(urls)) - 1:
                    raise last_error
                time.sleep(2 ** (attempt + 1))
        now = datetime.now(timezone.utc)
        version = row["version"] or f"snapshot-{now:%Y-%m-%d}"
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", source["slug"]):
            raise ValueError("Invalid report slug")
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", version):
            raise ValueError("Invalid version")
        path = ROOT / "pdfs" / row["vendor"] / f"{source['slug']}--{version}.pdf"
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            path = path.with_stem(f"{path.stem}--{digest[:8]}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            temporary = path.with_suffix(".part")
            temporary.write_bytes(data)
            temporary.replace(path)
        row.update(version=version, local_path=path.relative_to(ROOT).as_posix(),
                   retrieved_at=now.isoformat(timespec="seconds"), sha256=digest,
                   size_bytes=str(len(data)), pages=str(pages), status="archived")
        print(f"OK {row['vendor']}: {row['title']} ({len(data) / 1048576:.2f} MiB)", flush=True)
    except Exception as error:
        # A failed refresh must not discard the previously archived artifact.
        if old and old["status"] == "archived":
            return {**old, "notes": f"Refresh failed: {error}; {source.get('notes', '')}"}
        row["status"] = "oversized" if "exceeds" in str(error) and "MiB" in str(error) else "failed"
        row["notes"] = f"{row['notes']} Download failed: {type(error).__name__}: {error}".strip()
        print(f"FAIL {row['vendor']}: {row['title']}: {error}", flush=True)
    return row


def write_catalog(rows):
    rows.sort(key=lambda x: (x["vendor"], x["published_date"], x["title"], x["version"]))
    with (ROOT / "catalog.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def render(rows):
    archived = [row for row in rows if row["status"] == "archived"]
    publisher_count = len({row["vendor"] for row in archived})
    lines = ["# AI Frontier", "", "**Read the reports behind frontier AI.**", "",
             "[Chinese](README_CN.md) · [Browse reports](#browse-by-publisher) · [Full catalog](catalog.csv)", "",
             "Official technical reports, model cards, and system cards from leading AI labs, "
             "collected in one place. A reference shelf for researchers, engineers, and anyone "
             "who wants to understand how models are built, evaluated, and released.", "",
             f"**{len(archived)} original PDFs · {publisher_count} publishers · 2022 onward**", "",
             "**Star this repo to keep the reports within reach.**", "",
             "## Start reading", "",
             "Open a report below, or browse a publisher's full collection.", ""]
    cn_lines = ["# AI Frontier", "", "**读懂前沿 AI，从原始报告开始。**", "",
                "[英文版](README.md) · [按厂商浏览](#按厂商浏览) · [完整索引](catalog.csv)", "",
                "把散落在官网、模型仓库和 arXiv 的官方技术报告、模型卡与系统卡，整理成一份随时可查的资料库。"
                "为研究者、工程师和关心 AI 技术的人，保留理解模型如何训练、评测与发布的第一手材料。", "",
                f"**{len(archived)} 份原始 PDF · {publisher_count} 家厂商 · 2022 年起**", "",
                "**如果这份资料库对你有用，欢迎 Star 收藏，给下一次读报告留一个入口。**", "",
                "## 从这些报告开始", "",
                "直接打开下面的代表性报告，或进入厂商目录浏览更多资料。", ""]
    featured = [
        ("GPT-4 Technical Report", "GPT-4"),
        ("DeepSeek-V3 Technical Report", "DeepSeek-V3"),
        ("DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", "DeepSeek-R1"),
        ("The Llama 3 Herd of Models", "Llama 3"),
        ("Qwen3 Technical Report", "Qwen3"),
    ]
    by_title = {row["title"]: row for row in archived}
    links = [f"[{label}]({by_title[title]['local_path']})" for title, label in featured if title in by_title]
    if links:
        lines += [" · ".join(links), ""]
        cn_lines += [" · ".join(links), ""]
    lines += ["## Browse by publisher", "",
              "Pick a lab to find its archived reports and official source links. "
              "Each directory is ordered by recorded first publication date, newest first.", "",
              "| Publisher | PDFs |", "| --- | ---: |"]
    cn_lines += ["## 按厂商浏览", "",
                 "点击厂商名称，查看归档 PDF 与官方来源。目录按已记录的首次发布日期从新到旧排列。", "",
                 "| 厂商 | PDF 数量 |", "| --- | ---: |"]
    for vendor, label in VENDORS.items():
        vendor_rows = [row for row in rows if row["vendor"] == vendor]
        good = [row for row in vendor_rows if row["status"] == "archived"]
        english_label = "Z.ai / Zhipu AI" if vendor == "zai" else label
        lines.append(f"| [{english_label}](pdfs/{vendor}/README.md) | {len(good)} |")
        cn_lines.append(f"| [{label}](pdfs/{vendor}/README.md) | {len(good)} |")
        directory = ROOT / "pdfs" / vendor
        directory.mkdir(parents=True, exist_ok=True)
        detail = [f"# {label}", "", "按报告首次发布日期从新到旧排列；日期不明的条目置于最后。",
                  "日期仅精确到月份时保留 YYYY-MM，不推测具体日。", "",
                  "| 首次发布日期 | 报告 | 类型 | 归档版本 | 官方来源 |",
                  "| --- | --- | --- | --- | --- |"]
        for row in sorted(vendor_rows, key=lambda x: (x["published_date"], x["title"]), reverse=True):
            title = row["title"].replace("|", "\\|")
            link = f"[{title}]({Path(row['local_path']).name})" if row["status"] == "archived" else title + "（待补齐）"
            detail.append(f"| {row['published_date'] or '未确认'} | {link} | {row['document_type']} | {row['version'] or '—'} | [来源]({row['source_url']}) |")
        detail += ["", "文件校验值、抓取时间与版本更新时间见 [catalog.csv](../../catalog.csv)。", ""]
        (directory / "README.md").write_text("\n".join(detail), encoding="utf-8")
    lines += ["", "## Why keep this archive handy?", "",
              "- **Go straight to the source.** Original publisher PDFs and official links, together in one index.",
              "- **Compare across labs.** Find training methods, evaluation results, and safety disclosures "
              "across technical reports and model cards.",
              "- **Trace what changed.** Publication dates and revisions are recorded separately; "
              "older archived versions are retained when reports are updated.", "",
              "The [full catalog](catalog.csv) includes dates, versions, sources, and file verification details. "
              "Known omissions and uncertain dates are listed in [coverage and gaps](GAPS.md) "
              "(currently maintained in Chinese). Publisher directory notes are also currently in Chinese; "
              "report titles and original PDFs retain their source language.", "",
              "## Help build the reference shelf", "",
              "Found a missing report, a newer revision, or a broken link? "
              "Open an issue or pull request with the report title, publisher, and official source. "
              "A single good source link helps make the collection more useful for everyone.", "",
              "If this archive saves you a search, give it a **Star** or share it with someone reading AI papers.", "",
              "## Where this is heading", "",
              "The foundation is the original PDF archive. Planned next steps:", "",
              "- Readable Markdown versions that preserve tables, formulas, and figures.",
              "- Structured extraction of the technical details disclosed in each report.",
              "- A GitHub Pages interface for browsing by publisher and publication date.", "",
              "These are planned additions; the current collection provides PDFs and their index.", "",
              "## Scope and attribution", "",
              "This growing collection covers official model and model-family reports from 2022 onward, "
              "including technical reports, model cards, and system cards. Sources are publisher websites, "
              "official repositories, and author-submitted arXiv papers. Coverage is not yet exhaustive. "
              "For arXiv entries, the recorded first publication date is the first submission date; "
              "unknown dates are left unspecified.", "",
              "PDFs are preserved as provided by their publishers. Copyrights and terms of use remain "
              "with the original rights holders; this repository does not relicense the reports.", "",
              "Maintenance and implementation notes: [agent.md](agent.md).", ""]
    cn_lines += ["", "## 为什么值得收藏？", "",
                 "- **直接读原文。** 原始 PDF 与官方来源集中整理，减少在官网、仓库和论文页面之间来回查找。",
                 "- **横向看技术。** 对照不同厂商披露的训练方法、评测结果与安全信息，为自己的研究和判断找到依据。",
                 "- **回看演进。** 首次发布与修订日期分别记录，报告更新时保留已有归档版本，方便追溯变化。", "",
                 "[完整索引](catalog.csv) 提供日期、版本、来源及文件校验信息；"
                 "[覆盖范围与待补清单](GAPS.md) 公开记录遗漏、未确认日期和待核对范围。", "",
                 "## 一起把资料库补齐", "",
                 "发现遗漏报告、新修订版本或失效链接？欢迎通过 Issue 或 Pull Request 提供报告标题、厂商和官方来源。"
                 "一条可靠的线索，就能帮助更多人找到原始材料。", "",
                 "如果它帮你省下了一次搜索，欢迎 **Star**，也可以分享给正在读 AI 论文的朋友。", "",
                 "## 接下来，我们想做到", "",
                 "先把原始资料留好，再逐步让它更容易阅读和研究：", "",
                 "- 转为便于阅读和处理的 Markdown，保留表格、公式与图片。",
                 "- 结构化提取每份报告实际披露的技术细节。",
                 "- 建立 GitHub Pages 页面，按厂商和发布时间浏览。", "",
                 "以上为后续计划；当前已提供原始 PDF 与报告索引。", "",
                 "## 收录范围与版权", "",
                 "收录 2022 年起模型及模型家族的官方技术报告、模型卡与系统卡，来源包括厂商官网、官方仓库和作者提交的 arXiv 论文。"
                 "资料库仍在补齐，不代表已穷尽所有历史报告。arXiv 条目以首次提交日作为已记录的首次发布日期，未知日期不作推测。", "",
                 "PDF 保留发布者提供的原始内容，版权及使用条款归原权利人所有，本仓库不另行授权这些报告。", "",
                 "维护流程与实现说明见 [agent.md](agent.md)（英文）。", ""]
    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "README_CN.md").write_text("\n".join(cn_lines), encoding="utf-8")
    gaps = ["# 待补齐清单", "", "本清单区分已发现的缺口和首轮尚未覆盖的范围；不把未核对的资料标为已收齐。", "",
            "## 已登记条目", "", "| 厂商 | 报告 | 状态 | 原因 / 来源 |", "| --- | --- | --- | --- |"]
    for row in rows:
        if row["status"] != "archived" or not row["published_date"] or "Refresh failed:" in row["notes"]:
            note = row["notes"].replace("|", "\\|").replace("\n", " ")
            if not row["published_date"]:
                note = f"首次发布日期未确认。{note}"
            gaps.append(f"| {VENDORS[row['vendor']]} | {row['title']} | {row['status']} | {note or '首次发布日期未确认'}；[来源]({row['source_url']}) |")
    coverage = ROOT / "coverage-notes.md"
    if coverage.exists():
        gaps += ["", "## 首轮覆盖说明", "", coverage.read_text(encoding="utf-8").strip()]
    gaps.append("")
    (ROOT / "GAPS.md").write_text("\n".join(gaps), encoding="utf-8")


def verify(rows):
    errors = []
    if not any(row["status"] == "archived" for row in rows):
        errors.append("No archived PDFs in catalog")
    hashes = {}
    paths = set()
    for row in rows:
        if row["status"] != "archived":
            continue
        try:
            path = ROOT / row["local_path"]
            data = path.read_bytes()
            digest, pages = inspect_pdf(data)
            if digest != row["sha256"] or len(data) != int(row["size_bytes"]) or pages != int(row["pages"]):
                raise ValueError("Catalog checksum/size/page count mismatch")
            if digest in hashes and hashes[digest] != row["local_path"]:
                raise ValueError(f"Duplicate PDF bytes: {hashes[digest]}")
            hashes[digest] = row["local_path"]
            paths.add(row["local_path"])
        except Exception as error:
            errors.append(f"{row['local_path']}: {error}")
    for path in (ROOT / "pdfs").rglob("*.pdf"):
        if path.relative_to(ROOT).as_posix() not in paths:
            errors.append(f"Unindexed PDF: {path.relative_to(ROOT)}")
    for error in errors:
        print(error)
    print(f"Verified {len(paths)} PDFs; {len(errors)} integrity errors; {sum(r['status'] != 'archived' for r in rows)} recorded gaps.")
    return bool(errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["fetch", "verify", "render"])
    parser.add_argument("--vendor", choices=VENDORS)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    rows = read_catalog()
    if args.command == "verify":
        raise SystemExit(verify(rows))
    if args.command == "fetch":
        sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
        keys = [(s["vendor"], s["slug"]) for s in sources]
        if len(keys) != len(set(keys)) or any(s["vendor"] not in VENDORS for s in sources):
            raise ValueError("Duplicate source slugs or unsupported vendor")
        selected = [s for s in sources if not args.vendor or s["vendor"] == args.vendor]
        previous = {(r["vendor"], r["pdf_url"]): r for r in rows}
        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for result in executor.map(lambda s: fetch_one(s, previous, args.refresh), selected):
                results.append(result)
        # Keep older versions even when the input list now points to a new version.
        current_paths = {r["local_path"] for r in results if r["local_path"]}
        selected_keys = {(s["vendor"], s["pdf_url"]) for s in selected}
        selected_names = {(s["vendor"], s["title"]) for s in selected}
        rows = [r for r in rows if r["local_path"] not in current_paths and
                (r["status"] == "archived" or ((r["vendor"], r["pdf_url"]) not in selected_keys and
                 (r["vendor"], r["title"]) not in selected_names))] + results
        write_catalog(rows)
    render(rows)


if __name__ == "__main__":
    main()
