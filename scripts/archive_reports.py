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
DOCUMENT_TYPES = {
    "technical_report": ("Technical Report", "technical-reports.md"),
    "model_card": ("Model Card", "model-cards.md"),
    "system_card": ("System Card", "system-cards.md"),
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
        # Retrieval dates belong in the catalog, not in the public filename.
        name = source["slug"] if re.fullmatch(r"snapshot-\d{4}-\d{2}-\d{2}", version) else f"{source['slug']}--{version}"
        type_directory = Path(DOCUMENT_TYPES[row["document_type"]][1]).stem
        path = ROOT / "pdfs" / row["vendor"] / type_directory / f"{name}.pdf"
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
    brand = json.loads((ROOT / ".github" / "brand.json").read_text(encoding="utf-8"))
    lines = [f"# {brand['name']}", "", "![AI Frontier](assets/branding/ai-frontier-banner.png)", "", f"**{brand['tagline']}**", "",
             "[Chinese](README_CN.md) · [Browse publishers](#browse-by-publisher) · [Browse document types](#choose-the-right-document) · [Full catalog](catalog.csv)", "",
             "An open research archive for understanding how frontier AI models are built, evaluated, and deployed. "
             "We bring official technical reports, model cards, and system cards into one place, "
             "and are building toward readable sources, grounded technical analysis, and ongoing release tracking.", "",
             f"**{len(archived)} original PDFs · {publisher_count} publishers · 2022 onward**", "",
             "**Available today:** the original PDF archive and its verified source index. "
             "Markdown editions, structured analysis, and automated tracking are the next stages.", "",
             "**Star AI Frontier to keep the sources close and follow the archive as it grows.**", ""]
    cn_lines = [f"# {brand['name']}", "", "![AI Frontier](assets/branding/ai-frontier-banner.png)", "", f"**{brand['tagline_cn']}**", "",
                "[英文版](README.md) · [按厂商浏览](#按厂商浏览) · [按类型浏览](#按类型找报告) · [完整索引](catalog.csv)", "",
                "一个帮助研究者、工程师和 AI 技术读者理解模型如何训练、评测与部署的开放研究资料库。"
                "我们把散落在官网、模型仓库和 arXiv 的官方技术报告、模型卡与系统卡集中整理，"
                "并逐步推进可读原文、基于来源的技术分析与模型发布追踪。", "",
                f"**{len(archived)} 份原始 PDF · {publisher_count} 家厂商 · 2022 年起**", "",
                "**当前已提供：**原始 PDF 归档与经过核对的来源索引。Markdown、结构化分析与自动跟进是接下来的建设阶段。", "",
                "**Star 收藏 AI Frontier，把原始资料留在手边，也关注它如何逐步成为技术研究入口。**", ""]
    type_counts = {kind: sum(row["document_type"] == kind for row in archived) for kind in DOCUMENT_TYPES}
    lines += ["## Choose the right document", "",
              "Looking for implementation details, model boundaries, or deployment safety? Start with the corresponding document type.", "",
              "| Type | Main subject | Focus | Typical contents | PDFs |",
              "| --- | --- | --- | --- | ---: |",
              f"| [Technical Report](reports/technical-reports.md) | Model / training method | Implementation and experiments | Architecture, data, training, post-training, inference, benchmarks | {type_counts['technical_report']} |",
              f"| [Model Card](reports/model-cards.md) | Individual model | Model description and usage boundaries | Capabilities, limitations, intended and unsuitable uses, evaluations, safety information | {type_counts['model_card']} |",
              f"| [System Card](reports/system-cards.md) | Complete product / system | Risk, safety, and deployment behavior | Red teaming, dangerous capability evaluations, jailbreaks, safety mitigations, deployment restrictions | {type_counts['system_card']} |", "",
              "These are typical distinctions, not rigid boundaries. Documents can overlap or cover a model family; "
              "classification follows the publisher's designation and the document's primary purpose.", ""]
    cn_lines += ["## 按类型找报告", "",
                 "想看技术实现、模型使用边界，还是产品部署安全？从对应类型开始。", "",
                 "| 类型 | 主要对象 | 重点 | 常见内容 | PDF 数量 |",
                 "| --- | --- | --- | --- | ---: |",
                 f"| [Technical Report](reports/technical-reports.md) | 模型/训练方法 | 技术实现与实验 | 架构、数据、训练、后训练、推理、benchmark | {type_counts['technical_report']} |",
                 f"| [Model Card](reports/model-cards.md) | 单个模型 | 模型说明与使用边界 | 能力、限制、适用场景、不适用场景、评测、安全信息 | {type_counts['model_card']} |",
                 f"| [System Card](reports/system-cards.md) | 完整产品/系统 | 风险、安全、部署表现 | red teaming、危险能力评估、越狱、安全 mitigations、部署限制 | {type_counts['system_card']} |", "",
                 "这是常见区分，文档内容可能交叉，也可能覆盖整个模型家族；分类以官方命名与文档主要用途为准。", ""]
    lines += ["## Browse by publisher", "",
              "Pick a lab to find its archived reports and official source links. "
              "Each publisher has separate Technical Report, Model Card, and System Card folders. "
              "Each directory is ordered by recorded first publication date, newest first.", "",
              "Click a count to open that publisher's collection for the document type. Counts include archived PDFs only.", "",
              "| Publisher | Technical Reports | Model Cards | System Cards | Total PDFs |", "| --- | ---: | ---: | ---: | ---: |"]
    cn_lines += ["## 按厂商浏览", "",
                 "点击厂商名称，查看归档 PDF 与官方来源。每家厂商下按 Technical Report、Model Card、System Card 设独立子目录，"
                 "目录按已记录的首次发布日期从新到旧排列。", "",
                 "点击数量可进入该厂商对应类型的目录，数量仅统计已归档 PDF。", "",
                 "| 厂商 | 技术报告 | 模型卡 | 系统卡 | PDF 总数 |", "| --- | ---: | ---: | ---: | ---: |"]
    type_labels_cn = {"technical_report": "技术报告", "model_card": "模型卡", "system_card": "系统卡"}
    for vendor, label in VENDORS.items():
        vendor_rows = [row for row in rows if row["vendor"] == vendor]
        good = [row for row in vendor_rows if row["status"] == "archived"]
        english_label = "Z.ai / Zhipu AI" if vendor == "zai" else label
        count_links = []
        for kind, (_, filename) in DOCUMENT_TYPES.items():
            count = sum(row["document_type"] == kind for row in good)
            count_links.append(f"[{count}](pdfs/{vendor}/{Path(filename).stem}/README.md)")
        counts = " | ".join(count_links)
        lines.append(f"| [{english_label}](pdfs/{vendor}/README.md) | {counts} | {len(good)} |")
        cn_lines.append(f"| [{label}](pdfs/{vendor}/README.md) | {counts} | {len(good)} |")
        directory = ROOT / "pdfs" / vendor
        directory.mkdir(parents=True, exist_ok=True)
        detail = [f"# {english_label}", "", "[Home](../../README.md) · [中文首页](../../README_CN.md)", "",
                  "Reports are ordered by recorded first publication date, newest first; unknown dates appear last. "
                  "Month-only dates retain YYYY-MM precision. See the [document-type guide](../../README.md#choose-the-right-document).", "",
                  "按已记录的首次发布日期从新到旧排列，日期未确认的条目置于最后。日期仅精确到月份时保留 YYYY-MM，不推测具体日。"
                  "类型说明见 [公众文档](../../README_CN.md#按类型找报告)。", "",
                  "## Browse by type / 按类型浏览", "", "| Type / 类型 | Archived PDFs / 已归档 PDF |", "| --- | ---: |"]
        indexes = [(directory, detail, vendor_rows)]
        for kind, (type_label, filename) in DOCUMENT_TYPES.items():
            type_directory = directory / Path(filename).stem
            type_directory.mkdir(parents=True, exist_ok=True)
            entries = [row for row in vendor_rows if row["document_type"] == kind]
            count = sum(row["status"] == "archived" for row in entries)
            detail.append(f"| [{type_label} / {type_labels_cn[kind]}]({type_directory.name}/README.md) | {count} |")
            type_detail = [f"# {english_label} — {type_label}", "", "[Back to publisher / 返回厂商目录](../README.md)", "",
                           f"**{count} archived PDFs**. Ordered by recorded first publication date, newest first; unknown dates appear last.", "",
                           f"已归档 **{count} 份 PDF**。按已记录的首次发布日期从新到旧排列，日期未确认的条目置于最后。", ""]
            if not entries:
                type_detail += ["No documents of this type have been added yet. Contributions with official source links are welcome.", "",
                                "此类文档暂未收录，欢迎补充官方来源。", ""]
            indexes.append((type_directory, type_detail, entries))
        detail += ["", "## All reports / 全部报告", ""]
        for index_directory, index_lines, entries in indexes:
            prefix = "../../" if index_directory == directory else "../../../"
            index_lines += ["| First published / 首次发布日期 | Report / 报告 | Type / 类型 | Official source / 官方来源 |", "| --- | --- | --- | --- |"]
            for row in sorted(entries, key=lambda x: (x["published_date"], x["title"]), reverse=True):
                title = row["title"].replace("|", "\\|")
                if row["status"] == "archived":
                    relative_path = (ROOT / row["local_path"]).relative_to(index_directory).as_posix()
                    link = f"[{title}]({relative_path})"
                else:
                    link = title + " (Pending / 待补齐)"
                type_label, type_file = DOCUMENT_TYPES[row["document_type"]]
                index_lines.append(f"| {row['published_date'] or 'Unknown / 未确认'} | {link} | [{type_label} / {type_labels_cn[row['document_type']]}]({prefix}reports/{type_file}) | [Source / 来源]({row['source_url']}) |")
            index_lines += ["", f"Archive versions, checksums, retrieval times, and revision dates: [catalog.csv]({prefix}catalog.csv).", "",
                            f"归档版本、文件校验值、抓取时间与版本更新时间见 [catalog.csv]({prefix}catalog.csv)。", ""]
            (index_directory / "README.md").write_text("\n".join(index_lines), encoding="utf-8")
    report_directory = ROOT / "reports"
    report_directory.mkdir(parents=True, exist_ok=True)
    for kind, (type_label, filename) in DOCUMENT_TYPES.items():
        entries = [row for row in rows if row["document_type"] == kind]
        detail = [f"# {type_label}", "", "[All reports](../README.md) · [Document types](../README.md#choose-the-right-document)", "",
                  f"**{type_counts[kind]} archived PDFs**. Listed by recorded first publication date, newest first; unknown dates appear last.", "",
                  "| First published | Publisher | Report | Status | Official source |",
                  "| --- | --- | --- | --- | --- |"]
        for row in sorted(entries, key=lambda x: (x["published_date"], x["title"]), reverse=True):
            title = row["title"].replace("|", "\\|")
            link = f"[{title}](../{row['local_path']})" if row["status"] == "archived" else title
            label = "Z.ai / Zhipu AI" if row["vendor"] == "zai" else VENDORS[row["vendor"]]
            detail.append(f"| {row['published_date'] or 'Unknown'} | {label} | {link} | {row['status']} | [Source]({row['source_url']}) |")
        detail += ["", "Versions, retrieval dates, and verification details: [catalog.csv](../catalog.csv).", ""]
        (report_directory / filename).write_text("\n".join(detail), encoding="utf-8")
    lines += ["", "## Why follow AI Frontier?", "",
              "- **Go straight to the source.** Original publisher PDFs and official links, together in one index.",
              "- **Compare across labs.** Find training methods, evaluation results, and safety disclosures "
              "across technical reports and model cards.",
              "- **Trace what changed.** Publication dates and revisions are recorded separately; "
              "older archived versions are retained when reports are updated.", "",
              "The [full catalog](catalog.csv) includes dates, versions, sources, and file verification details. "
              "Known omissions and uncertain dates are listed in [coverage and gaps](GAPS.md) "
              "(currently maintained in Chinese). Publisher and document-type directory READMEs are English-first bilingual; "
              "report titles and original PDFs retain their source language.", "",
              "## Help build the reference shelf", "",
              "Found a missing report, a newer revision, or a broken link? "
              "Open an issue or pull request with the report title, publisher, and official source. "
              "A single good source link helps make the collection more useful for everyone.", "",
              "If this archive saves you a search, give it a **Star** or share it with someone reading AI papers.", "",
              "## From sources to insight", "",
              "The original reports are the foundation. The longer-term goal is a research workflow "
              "that helps readers follow releases, inspect technical evidence, and understand what changed.", "",
              "| Stage | What it helps you do | Status |", "| --- | --- | --- |",
              "| Original sources | Find official reports, source links, dates, and archived revisions | Available |",
              "| Readable sources | Read and process Markdown with tables, formulas, and figures preserved | Planned |",
              "| Technical analysis | Examine architecture, data, training, post-training, inference, and evaluation details with source references | Planned |",
              "| Continuous tracking | Follow new model releases and report revisions through automated monitoring and update histories | Planned |", "",
              "A GitHub Pages browsing experience is also planned. Today, sources are curated manually; "
              "the archive provides original PDFs, indexes, and explicit coverage gaps.", "",
              "## Scope and attribution", "",
              "This growing collection covers official model and model-family reports from 2022 onward, "
              "including technical reports, model cards, and system cards. Sources are publisher websites, "
              "official repositories, and author-submitted arXiv papers. Coverage is not yet exhaustive. "
              "For arXiv entries, the recorded first publication date is the first submission date; "
              "unknown dates are left unspecified.", "",
              "PDFs are preserved as provided by their publishers. Copyrights and terms of use remain "
              "with the original rights holders; this repository does not relicense the reports.", "",
              "Maintenance and implementation notes: [agent.md](agent.md).", ""]
    cn_lines += ["", "## 为什么值得持续关注？", "",
                 "- **直接读原文。** 原始 PDF 与官方来源集中整理，减少在官网、仓库和论文页面之间来回查找。",
                 "- **横向看技术。** 对照不同厂商披露的训练方法、评测结果与安全信息，为自己的研究和判断找到依据。",
                 "- **回看演进。** 首次发布与修订日期分别记录，报告更新时保留已有归档版本，方便追溯变化。", "",
                 "[完整索引](catalog.csv) 提供日期、版本、来源及文件校验信息；"
                 "[覆盖范围与待补清单](GAPS.md) 公开记录遗漏、未确认日期和待核对范围。", "",
                 "## 一起把资料库补齐", "",
                 "发现遗漏报告、新修订版本或失效链接？欢迎通过 Issue 或 Pull Request 提供报告标题、厂商和官方来源。"
                 "一条可靠的线索，就能帮助更多人找到原始材料。", "",
                 "如果它帮你省下了一次搜索，欢迎 **Star**，也可以分享给正在读 AI 论文的朋友。", "",
                 "## 从原始资料走向技术洞察", "",
                 "原始报告是基础。我们希望逐步建立一条研究路径，帮助读者跟进发布、核对技术证据、理解模型发生了什么变化。", "",
                 "| 阶段 | 帮助你做什么 | 状态 |", "| --- | --- | --- |",
                 "| 原始资料 | 查找官方报告、来源链接、日期与归档版本 | 已提供 |",
                 "| 可读原文 | 阅读和处理 Markdown，保留表格、公式与图片 | 计划中 |",
                 "| 技术分析 | 结合原文出处，研究架构、数据、训练、后训练、推理与评测细节 | 计划中 |",
                 "| 持续跟进 | 通过自动监测与更新记录，追踪新模型发布及报告修订 | 计划中 |", "",
                 "GitHub Pages 浏览页面也在规划中。当前来源由人工核对与维护，已提供原始 PDF、索引和明确的覆盖缺口。", "",
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
        if (len(keys) != len(set(keys)) or any(s["vendor"] not in VENDORS for s in sources)
                or any(s["document_type"] not in DOCUMENT_TYPES for s in sources)):
            raise ValueError("Duplicate source slugs, unsupported vendor, or unsupported document type")
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
