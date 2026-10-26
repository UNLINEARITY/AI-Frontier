"""Export persistent TextFold packages from the existing OCR archive, without model calls."""
import argparse
import csv
import json
from pathlib import Path

from textfold_sources import UPSTREAM, checksum, load_textfold_index, prepare_document

ROOT = Path(__file__).resolve().parents[1]


def prepare(root, vendors=(), slugs=(), force=False):
    with (root / 'catalog.csv').open(encoding='utf-8', newline='') as stream:
        rows = [r for r in csv.DictReader(stream) if r['status'] == 'archived']
    by_pdf = {r.get('source_pdf'): r for r in json.loads((root / 'abstracts/index.json').read_text())['reports']
              if r.get('source_pdf')}
    # An edited review is an input to re-export, rather than corruption of the
    # old document. Its recorded hash is refreshed only after replay succeeds.
    old = load_textfold_index(root, rows, verify_cleanup=False)
    complete, prepared, skipped = dict(old), 0, 0
    for row in rows:
        summary = by_pdf.get(row['local_path'])
        slug = summary['id'].split(':', 1)[1] if summary else Path(row['local_path']).stem + '--source-' + row['sha256'][:8]
        if vendors and row['vendor'] not in vendors or slugs and slug not in slugs:
            continue
        report_id = f'{row["vendor"]}:{slug}'
        existing = old.get(report_id)
        cleanup = root / 'reader-content' / row['vendor'] / slug / 'cleanup.json'
        cleanup_hash = checksum(cleanup) if cleanup.is_file() else None
        if (not force and existing and existing['source_pdf'] == row['local_path'] and existing['source_sha256'] == row['sha256']
                and (root / existing['ocr_markdown']).is_file()
                and checksum(root / existing['ocr_markdown']) == existing['ocr_sha256']
                and cleanup_hash == existing.get('text_cleanup', {}).get('sha256')):
            skipped += 1
            continue
        record = prepare_document(root, row, summary)
        # Re-exporting unchanged source table crops must retain their verified
        # visual review; changed crops still require a new review.
        previous_images = {asset['path']: asset for asset in (existing or {}).get('images', [])}
        for asset in record['images']:
            previous = previous_images.get(asset['path'], {})
            if (asset.get('recovery') and previous.get('visual_review')
                    and all(previous.get(key) == asset.get(key) for key in
                            ('sha256', 'source_sha256', 'physical_page', 'bbox_pdf_points'))):
                asset['visual_review'] = True
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
    parser.add_argument('--force', action='store_true',
                        help='re-export matched packages even when source, OCR and review are unchanged')
    args = parser.parse_args()
    prepare(ROOT, args.vendor, args.slug, force=args.force)
