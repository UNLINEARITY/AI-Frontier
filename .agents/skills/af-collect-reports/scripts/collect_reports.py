#!/usr/bin/env python3
"""Collect explicitly selected registered reports with the existing downloader."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
import archive_reports as archive


def collect(vendor, slugs, refresh=False):
    sources = json.loads((archive.ROOT / 'sources.json').read_text())
    selected = [s for s in sources if s['vendor'] == vendor and s['slug'] in slugs]
    missing = set(slugs) - {s['slug'] for s in selected}
    if missing or len(selected) != len(set(slugs)):
        raise ValueError(f'Unknown or duplicate source registration: {sorted(missing)}')
    rows = archive.read_catalog()
    previous = {(r['vendor'], r['pdf_url']): r for r in rows}
    results = [archive.fetch_one(source, previous, refresh) for source in selected]
    paths = {r['local_path'] for r in results if r['local_path']}
    keys = {(s['vendor'], s['pdf_url']) for s in selected}
    names = {(s['vendor'], s['title']) for s in selected}
    # Match the main CLI's preservation rule: replace current results, retain history.
    retained = [r for r in rows if r['local_path'] not in paths and
                (r['status'] == 'archived' or ((r['vendor'], r['pdf_url']) not in keys
                                              and (r['vendor'], r['title']) not in names))]
    archive.write_catalog(retained + results)
    archive.render(retained + results)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor', required=True, choices=archive.VENDORS)
    parser.add_argument('--slug', action='append', required=True)
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    try:
        results = collect(args.vendor, args.slug, args.refresh)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'{error}\n')
    if any(r['status'] != 'archived' for r in results):
        parser.exit(1, 'Some selected reports remain unarchived; review the recorded gaps.\n')
