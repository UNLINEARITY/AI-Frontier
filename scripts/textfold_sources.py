"""Prepare source-bound, offline TextFold documents from the local OCR archive.

The exported package is independent of OCR/PDF/parser dependencies at site-build time.
TextFold's first-sentence fallback is used without importing its model or server code.
"""
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

UPSTREAM = {'name': 'TextFold', 'version': '0.10.7',
            'repository': 'https://github.com/chenxiachan/textfold',
            'commit': '2cd77e0987b590f9f67154bcdda76c59e6870b73'}


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_path(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to((root / 'reader-content').resolve()):
        raise ValueError(f'TextFold package path outside reader-content/: {value}')
    return path


def apply_text_cleanup(text, path, report_id, row, ocr_sha256):
    """Replay reviewed, exact replacements without changing the OCR source."""
    if not path.is_file():
        return text, None
    data = json.loads(path.read_text(encoding='utf-8'))
    if (data.get('schema_version') != 1 or data.get('id') != report_id
            or data.get('source_sha256') != row['sha256']
            or data.get('ocr_sha256') != ocr_sha256):
        raise ValueError(f'Stale OCR cleanup source: {report_id}')
    patches = data.get('patches')
    if not isinstance(patches, list):
        raise ValueError(f'Invalid OCR cleanup patches: {report_id}')
    original = text
    for patch in patches:
        before, after, count = patch.get('before'), patch.get('after'), patch.get('count', 1)
        pages = patch.get('pdf_pages')
        if (not isinstance(before, str) or not before or not isinstance(after, str) or before == after
                or type(count) is not int or count < 1 or text.count(before) != count
                or not isinstance(pages, list) or not pages
                or any(type(p) is not int or p < 1 or p > int(row.get('pages') or p) for p in pages)
                or not patch.get('evidence')):
            raise ValueError(f'Invalid or ambiguous OCR cleanup replacement: {report_id}')
        text = text.replace(before, after)
    # Cleanup cannot silently remove, replace or reorder source image embeds.
    image = re.compile(r'!\[[^\]\n]*\]\([^\n]+?\)|!\[\[[^\]\n]+\]\]|<img\b[^>]*>', re.I)
    if image.findall(original) != image.findall(text):
        raise ValueError(f'OCR cleanup changes source images: {report_id}')
    return text, {'sha256': checksum(path), 'patch_count': len(patches)}


def swallowed_pre_blocks(html):
    """Return code blocks that still contain document structure, i.e. OCR damage.

    OCR reads printed fences from prompt boxes and figures, so a source can open
    a code block that the renderer never closes. When that happens prose, tables
    and images are shown as code. Report those blocks instead of exporting them
    silently; the repair belongs in the document's reviewed cleanup.json.
    """
    found = []
    for block in re.findall(r'<pre\b[^>]*>(.*?)</pre>', html, re.S | re.I):
        text = re.sub(r'<[^>]+>', '', block)
        # Printed prompt boxes and model transcripts legitimately start lines with
        # "###", so only numbered section headings, tables and image embeds show
        # that document body content was swallowed by an unbalanced fence.
        numbered = len(re.findall(r'(?m)^#{2,6} \d+(?:\.\d+)*\s+\S', text))
        tables = len(re.findall(r'(?m)^\s*<table', text))
        images = len(re.findall(r'!\[(?!\[)[^\]\n]*\]\([^)\n]+\)', text))
        if numbered or tables or images:
            found.append({'numbered_headings': numbered, 'tables': tables, 'images': images,
                          'chars': len(text)})
    return found


def normalize_ocr_markdown(text):
    """Repair image syntax, numbered heading depth and math punctuation spacing."""
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1][0]
            elif marker[1][0] == fence:
                fence = None
            lines.append(line)
            continue
        if fence is None:
            line = re.sub(r'!\[\[([^\]|]+)(?:\|([^\]]*))?\]\]',
                          lambda m: f'![{m[2] or ""}]({m[1]})', line)
            heading = re.match(r'^#{1,6}\s+((?:\d+|[A-Z])(?:\.\d+)*)(?:\.)?\s+(.+)$', line)
            if heading:
                depth = min(6, 2 + heading[1].count('.'))
                line = '#' * depth + ' ' + heading[1] + ' ' + heading[2]
            # OCR keeps the PDF layout gap between a closing inline-math
            # delimiter and the punctuation that follows it.
            line = re.sub(r'(?<=\S)\$[ \t]+([,.;:!?\uff0c\u3002\uff1b\uff1a\uff01\uff1f])', r'$\1', line)
        lines.append(line)
    return '\n'.join(lines) + '\n'


def local_ladder(unit):
    """TextFold ladder.local/head_words, extracted to keep model code out of builds."""
    def head(tokens, limit):
        indices, count = [], 0
        is_word = lambda t: 'a' in t or 'x' in t or bool(re.search(r'\w', t.get('t', '')))
        for i, token in enumerate(tokens):
            if is_word(token) and count == limit:
                break
            indices.append(i)
            count += is_word(token)
        while indices and not is_word(tokens[indices[-1]]):
            indices.pop()
        return indices
    start, end = unit['sents'][0]
    brief = [dict(token, m=start + i) for i, token in enumerate(unit['toks'][start:end])]
    first = head(brief, 14)
    take = first[-1] + 1 if first else len(brief)
    topic = [{**{k: brief[i][k] for k in ('t', 'a', 'x', 's', 'f') if k in brief[i]}, 'k': i}
             for i in head(brief[:take], 3)]
    return {'role': 'context', 'ev': [0], 'brief': brief, 'tn': take, 'topic': topic, 'model': 'local'}


def repair_table_images(source_html, workspace, recover_table=None):
    """Use MinerU's whole-table image when nested HTML images were not exported.

    The immutable Markdown and source images are retained. The replacement uses
    the matching content-list block, never a guessed illustration or crop.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(source_html, 'lxml')
    repairs, blocks = [], None
    for table in list(soup.find_all('table')):
        missing = [img.get('src', '') for img in table.find_all('img')
                   if not (workspace / unquote(img.get('src', ''))).is_file()]
        if not missing:
            continue
        if blocks is None:
            blocks = json.loads((workspace / 'content_list_v2.json').read_text())
            if not isinstance(blocks, list):
                raise ValueError('Unsupported OCR content-list layout for table image recovery')
        block = next((b for b in blocks if b.get('type') == 'table'
                      and all(name in b.get('table_body', '') for name in missing)), None)
        image = block.get('img_path', '') if block else ''
        if block and (not image or not (workspace / image).is_file()) and recover_table:
            image = recover_table(block)
        if not image:
            raise ValueError(f'OCR table image missing, including whole-table crop: {missing}')
        if not image.startswith('assets/') and not (workspace / image).is_file():
            raise ValueError(f'OCR table image missing, including whole-table crop: {missing}')
        replacement = soup.new_tag('p')
        replacement.append(soup.new_tag('img', src=image, alt=''))
        table.replace_with(replacement)
        repairs.append({'method': 'recorded-whole-table-image', 'missing_nested_images': missing,
                        'img_path': image, 'page_idx': block.get('page_idx'), 'bbox': block.get('bbox')})
    return (soup.body or soup).decode_contents(), repairs


def prepare_document(root, row, summary=None, output_root=None):
    from PIL import Image
    from vendor.textfold import markdown, semantic
    from vendor.textfold.parse import parse

    root = Path(root).resolve()
    output_root = Path(output_root).resolve() if output_root else root / 'reader-content'
    pdf = root / row['local_path']
    if not pdf.is_file() or checksum(pdf) != row['sha256']:
        raise ValueError(f'PDF source checksum mismatch: {row["local_path"]}')
    if summary and (summary.get('source_pdf') != row['local_path'] or
                    summary.get('source_sha256') != row['sha256']):
        raise ValueError(f'Summary source mismatch: {row["local_path"]}')
    relative_pdf = Path(row['local_path']).relative_to('pdfs')
    workspace = root / 'ocr' / relative_pdf.with_suffix('')
    source = workspace / (relative_pdf.stem + '.md')
    text = source.read_text(encoding='utf-8-sig')
    vendor = row['vendor']
    # A catalog snapshot without a curated reader must not overwrite another
    # version whose canonical reader uses the same slug.
    slug = summary['id'].split(':', 1)[1] if summary else relative_pdf.stem + '--source-' + row['sha256'][:8]
    if not re.fullmatch(r'[a-z0-9_-]+', vendor) or not re.fullmatch(r'[a-z0-9_-]+', slug):
        raise ValueError('Unsafe TextFold document id')
    report_id = f'{vendor}:{slug}'
    folder = output_root / vendor / slug
    cleanup_path = folder / 'cleanup.json'
    text, cleanup = apply_text_cleanup(text, cleanup_path, report_id, row, checksum(source))
    if cleanup:
        cleanup['path'] = cleanup_path.relative_to(root).as_posix()
    images, seen, exported = [], {}, set()

    def resolve_image(raw):
        if raw in exported:
            return raw
        value = unquote(raw.split('#', 1)[0].split('?', 1)[0])
        image = (workspace / value).resolve()
        if (re.match(r'^[a-z][a-z0-9+.-]*:', value, re.I) or
                not image.is_relative_to((workspace / 'images').resolve()) or not image.is_file()):
            raise ValueError(f'OCR image outside source images/ or missing: {raw}')
        if image in seen:
            return seen[image]
        digest = checksum(image)
        target = folder / 'images' / f'{digest}.webp'
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(image) as im:
            im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
            if im.mode not in ('RGB', 'RGBA'):
                im = im.convert('RGBA')
            width, height = im.size
            im.save(target, 'WEBP', quality=90, method=4)
        site_path = f'assets/textfold-images/{vendor}/{slug}/{target.name}'
        images.append({'path': target.relative_to(root).as_posix(), 'sha256': checksum(target),
                       'source_path': image.relative_to(root).as_posix(), 'source_sha256': digest,
                       'site_path': site_path, 'width': width, 'height': height})
        seen[image] = site_path
        exported.add(site_path)
        return site_path

    def recover_table(block):
        import pymupdf
        bounds = block.get('bbox')
        page_index = block.get('page_idx')
        if (not isinstance(bounds, list) or len(bounds) != 4 or not isinstance(page_index, int)
                or not all(isinstance(v, (int, float)) and 0 <= v <= 1000 for v in bounds)):
            raise ValueError('OCR table recovery needs a recorded page and normalized bbox')
        with pymupdf.open(pdf) as document:
            page = document[page_index]
            rectangle = pymupdf.Rect(bounds[0] * page.rect.width / 1000,
                                     bounds[1] * page.rect.height / 1000,
                                     bounds[2] * page.rect.width / 1000,
                                     bounds[3] * page.rect.height / 1000)
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=rectangle, alpha=False)
            from io import BytesIO
            im = Image.open(BytesIO(pixmap.tobytes('png')))
            im.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
            signature = hashlib.sha256((row['sha256'] + str(page_index) + str(bounds)).encode()).hexdigest()
            target = folder / 'images' / f'table-{signature}.webp'
            target.parent.mkdir(parents=True, exist_ok=True)
            im.save(target, 'WEBP', quality=94, method=4)
            site_path = f'assets/textfold-images/{vendor}/{slug}/{target.name}'
            images.append({'path': target.relative_to(root).as_posix(), 'sha256': checksum(target),
                           'source_path': row['local_path'], 'source_sha256': row['sha256'],
                           'site_path': site_path, 'width': im.width, 'height': im.height,
                           'physical_page': page_index + 1, 'bbox_pdf_points': list(rectangle),
                           'visual_review': False, 'recovery': 'recorded-table-region'})
            exported.add(site_path)
            return site_path

    normalized_markdown = normalize_ocr_markdown(text)
    source_html, _ = markdown.to_html(normalized_markdown)
    swallowed = swallowed_pre_blocks(source_html)
    if swallowed:
        # Rendering prose as code is invisible in the build, so name the document
        # and let a reviewed cleanup.json repair the unbalanced fence.
        regions = ', '.join(f'{b["numbered_headings"]} headings/{b["tables"]} tables/'
                            f'{b["images"]} images/{b["chars"]} chars' for b in swallowed)
        print(f'WARNING: {report_id} renders document structure inside {len(swallowed)} code '
              f'block(s) ({regions}); review cleanup.json for this document.', file=sys.stderr)
    _, source_html = markdown.take_title(source_html, {}, source.name)
    source_html, table_repairs = repair_table_images(source_html, workspace, recover_table)
    normalized = semantic.normalize(source_html, resolve_img=resolve_image)
    meta = {'id': report_id, 'title': row['title'], 'authors': [], 'date': row.get('published_date', ''),
            'version': row.get('version', ''), 'abs_url': row['source_url'], 'html_url': row['source_url'],
            'source': {'kind': 'markdown', 'name': source.name}, 'source_sha256': row['sha256'],
            'label': row['title'], 'license': '', 'langs': ['en'], 'stale': [], 'versions': {},
            'local': True, 'ai_generated': False, 'folding': 'first-sentence'}
    doc = parse(normalized, meta)
    for unit in doc['units'].values():
        unit['lad'] = local_ladder(unit)
    doc['provenance'] = {'upstream': UPSTREAM, 'ai_generated': False, 'model': None,
                         'method': 'local-first-sentence', 'source_sha256': row['sha256'],
                         'ocr_sha256': checksum(source)}
    if cleanup:
        doc['provenance']['text_cleanup'] = cleanup
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / 'document.json.gz'
    target.write_bytes(gzip.compress(json.dumps(doc, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0))
    record = {'id': report_id, 'vendor': vendor, 'title': row['title'], 'version': row.get('version', ''),
            'source_pdf': row['local_path'], 'source_sha256': row['sha256'], 'source_url': row['source_url'],
            'ocr_markdown': source.relative_to(root).as_posix(), 'ocr_sha256': checksum(source),
            'document_path': target.relative_to(root).as_posix(), 'document_sha256': checksum(target),
            'sections': len(doc['chunks']), 'units': len(doc['units']), 'images': images,
            'table_image_fallbacks': table_repairs}
    if cleanup:
        record['text_cleanup'] = cleanup
    return record


def load_textfold_index(root, catalog, verify_cleanup=True):
    """Validate published packages; deliberately never read OCR sources or PDFs."""
    root = Path(root)
    index = root / 'reader-content/index.json'
    if not index.exists():
        return {}
    data = json.loads(index.read_text())
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported TextFold index schema')
    by_pdf = {row['local_path']: row for row in catalog}
    result = {}
    for record in data['reports']:
        row = by_pdf.get(record['source_pdf'])
        if not row or record['source_sha256'] != row['sha256']:
            raise ValueError(f'Stale TextFold source checksum: {record["id"]}')
        if record['id'] in result:
            raise ValueError(f'Duplicate TextFold id: {record["id"]}')
        for asset in [dict(path=record['document_path'], sha256=record['document_sha256']), *record['images']]:
            path = package_path(root, asset['path'])
            if not path.is_file() or checksum(path) != asset['sha256']:
                raise ValueError(f'TextFold asset checksum mismatch: {asset["path"]}')
        cleanup = record.get('text_cleanup')
        if cleanup and verify_cleanup:
            path = package_path(root, cleanup['path'])
            if not path.is_file() or checksum(path) != cleanup['sha256']:
                raise ValueError(f'OCR cleanup checksum mismatch: {record["id"]}')
        result[record['id']] = record
    return result


def load_document(root, record):
    path = package_path(Path(root), record['document_path'])
    if checksum(path) != record['document_sha256']:
        raise ValueError(f'TextFold document checksum mismatch: {record["id"]}')
    doc = json.loads(gzip.decompress(path.read_bytes()))
    if doc['meta']['id'] != record['id'] or doc['meta']['source_sha256'] != record['source_sha256']:
        raise ValueError(f'TextFold document source mismatch: {record["id"]}')
    if doc.get('provenance', {}).get('text_cleanup') != record.get('text_cleanup'):
        raise ValueError(f'OCR cleanup provenance mismatch: {record["id"]}')
    return doc
