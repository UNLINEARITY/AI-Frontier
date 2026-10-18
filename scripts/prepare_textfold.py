"""Export persistent TextFold packages from the existing OCR archive, without model calls."""
import argparse
import csv
import json
from pathlib import Path

from textfold_sources import UPSTREAM, checksum, load_textfold_index, prepare_document

ROOT = Path(__file__).resolve().parents[1]


def prepare(root, vendors=(), slugs=()):
    rows = [r for r in csv.DictReader((root / 'catalog.csv').open()) if r['status'] == 'archived']
    by_pdf = {r.get('source_pdf'): r for r in json.loads((root / 'abstracts/index.json').read_text())['reports']
              if r.get('source_pdf')}
    old = load_textfold_index(root, rows)
    complete, prepared, skipped = dict(old), 0, 0
    for row in rows:
        summary = by_pdf.get(row['local_path'])
        slug = summary['id'].split(':', 1)[1] if summary else Path(row['local_path']).stem + '--source-' + row['sha256'][:8]
        if vendors and row['vendor'] not in vendors or slugs and slug not in slugs:
            continue
        report_id = f'{row["vendor"]}:{slug}'
        existing = old.get(report_id)
        if (existing and existing['source_pdf'] == row['local_path'] and existing['source_sha256'] == row['sha256']
                and (root / existing['ocr_markdown']).is_file()
                and checksum(root / existing['ocr_markdown']) == existing['ocr_sha256']):
            skipped += 1
            continue
        record = prepare_document(root, row, summary)
        complete[record['id']] = record
        prepared += 1
        index = root / 'reader-content/index.json'
        index.parent.mkdir(parents=True, exist_ok=True)
        content = {'schema_version': 1, 'upstream': UPSTREAM, 'folding': 'local-first-sentence',
                   'reports': sorted(complete.values(), key=lambda r: r['id'])}
        temporary = index.with_suffix('.tmp')
        temporary.write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(index)
        if prepared % 10 == 0:
            print(f'Prepared {prepared}; available {len(complete)}/{len(rows)}; skipped {skipped}', flush=True)
    print(f'TextFold packages: {len(complete)}; prepared {prepared}; reused {skipped}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor', action='append', default=[])
    parser.add_argument('--slug', action='append', default=[])
    args = parser.parse_args()
    prepare(ROOT, args.vendor, args.slug)
