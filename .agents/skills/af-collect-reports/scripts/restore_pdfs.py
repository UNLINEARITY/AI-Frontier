#!/usr/bin/env python3
"""Restore exact selected source bytes from the catalog; default is a dry run."""
import argparse
import csv
import hashlib
import json
import re
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore(root, vendor=None, slugs=(), download=False):
    root = root.resolve()
    reports = json.loads((root / 'abstracts/index.json').read_text())['reports']
    with (root / 'catalog.csv').open(newline='') as stream:
        rows = {r['local_path']: r for r in csv.DictReader(stream) if r['status'] == 'archived'}
    selected = [r for r in reports if r.get('source_kind') != 'html' and (not vendor or r['vendor'] == vendor)
                and (not slugs or r['id'].split(':', 1)[1] in slugs)]
    if not selected:
        raise ValueError('No selected abstracts source matches the filters')
    if slugs and set(slugs) - {r['id'].split(':', 1)[1] for r in selected}:
        raise ValueError('An unknown or unselected report slug was requested')
    result = []
    for report in selected:
        row = rows.get(report['source_pdf'])
        expected = report['source_sha256']
        if not row or row['sha256'] != expected or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError(f"Stale catalog binding: {report['id']}")
        relative = Path(report['source_pdf'])
        target = (root / relative).resolve()
        if relative.is_absolute() or relative.parts[0] != 'pdfs' or not target.is_relative_to(root.resolve()):
            raise ValueError('Source PDF must remain inside the local pdfs directory')
        if target.exists():
            if digest(target) != expected:
                raise ValueError(f'Existing local PDF has a different hash; not overwritten: {target}')
            result.append((report['id'], 'present'))
            continue
        if not download:
            result.append((report['id'], 'missing'))
            continue
        size = int(row['size_bytes'])
        if size <= 0:
            raise ValueError('Catalog source size must be positive')
        urls = list(dict.fromkeys(u for u in (row['pdf_url'], row['resolved_url']) if u))
        errors = []
        data = None
        for url in urls:
            if urlsplit(url).scheme != 'https':
                errors.append('Only registered HTTPS source URLs are accepted')
                continue
            try:
                request = urllib.request.Request(url, headers={'User-Agent': 'AI-Frontier-Source-Restore/1.0'})
                with urllib.request.urlopen(request, timeout=90) as response:
                    candidate = response.read(size + 1)
                if (len(candidate) != size or not candidate.startswith(b'%PDF-')
                        or hashlib.sha256(candidate).hexdigest() != expected):
                    raise ValueError('Downloaded bytes do not match the recorded original')
                data = candidate
                break
            except Exception as error:
                errors.append(str(error))
        if data is None:
            raise ValueError(f"Cannot restore {report['id']}: {'; '.join(errors) or 'no registered URL'}")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, suffix='.part', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
            temporary.replace(target)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
        result.append((report['id'], 'restored'))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--vendor')
    parser.add_argument('--slug', action='append', default=[])
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    try:
        for report_id, status in restore(args.root.resolve(), args.vendor, args.slug, args.download):
            print(f'{status}: {report_id}')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'{error}\n')
