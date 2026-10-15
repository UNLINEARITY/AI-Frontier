"""Resolve model identities for a release timeline, independently of report dates."""
from datetime import date
from urllib.parse import urlsplit


def model_key(vendor, name):
    return vendor, name.casefold()


def timeline_models(coverage, history, sources, vendors):
    from model_groups import CATEGORY_GROUPS, TAG_TO_GROUP
    source_ids = {(s['vendor'], s['slug']) for s in sources}
    coverage_ids = {model_key(m['vendor'], m['model']) for m in coverage['models']}
    aliases = {}
    for alias in history.get('coverage_aliases', []):
        key = model_key(alias['vendor'], alias['coverage_model'])
        if key not in coverage_ids or key in aliases or not alias['models']:
            raise ValueError(f'Invalid timeline coverage alias: {key}')
        aliases[key] = alias
    models = {}

    def add(record, names, inherit_date=True, inherit_reports=True, inherit_categories=True):
        vendor = record['vendor']
        if vendor not in vendors:
            raise ValueError(f'Unknown timeline publisher: {vendor}')
        for slug in record.get('report_slugs', []):
            if (vendor, slug) not in source_ids:
                raise ValueError(f'Unregistered timeline report: {vendor}/{slug}')
        for name in names:
            if not isinstance(name, str) or not name.strip():
                raise ValueError('Empty timeline model identity')
            key = model_key(vendor, name)
            entry = models.setdefault(key, dict(vendor=vendor, model=name, source_url=record['source_url'],
                                                report_slugs=[], release_date='', categories=[], reading_aliases=[], search_aliases=[]))
            entry['reading_aliases'] = list(dict.fromkeys(entry['reading_aliases'] + [record['model']]))
            if len(names) == 1:
                entry['search_aliases'] = list(dict.fromkeys(entry['search_aliases'] + [record['model']]))
            if inherit_reports:
                entry['report_slugs'] = list(dict.fromkeys(entry['report_slugs'] + record.get('report_slugs', [])))
            if inherit_categories:
                inherited = list(record.get('groups', []))
                for tag in record.get('latest_categories', []) + record.get('frontier_categories', []):
                    if tag in TAG_TO_GROUP:
                        inherited.append(TAG_TO_GROUP[tag])
                for group in inherited:
                    if group not in CATEGORY_GROUPS:
                        raise ValueError(f'Unknown timeline model group: {key}: {group}')
                    if group not in entry['categories']:
                        entry['categories'].append(group)
            released = record.get('release_date', '') if inherit_date else ''
            if released:
                if date.fromisoformat(released).isoformat() != released:
                    raise ValueError(f'Use a complete ISO model release date: {key}')
                if entry['release_date'] and entry['release_date'] != released:
                    raise ValueError(f'Conflicting model release dates: {key}')
                entry['release_date'] = released
                entry['release_source_url'] = record.get('release_source_url', record['source_url'])
                entry['release_evidence'] = record.get('release_evidence', record.get('note_en', ''))
                if not entry['release_evidence']:
                    raise ValueError(f'Missing model release evidence: {key}')
            for field in ('source_url', 'release_source_url'):
                if field in entry and urlsplit(entry[field]).scheme not in ('https', 'http'):
                    raise ValueError(f'Unsafe timeline source: {key}')

    # Curated history establishes canonical names and model-specific report associations.
    for model in history.get('models', []):
        key = model_key(model['vendor'], model['model'])
        if key in models:
            raise ValueError(f'Duplicate historical model: {key}')
        add(model, [model['model']])
    for model in coverage['models']:
        alias = aliases.get(model_key(model['vendor'], model['model']), {})
        names = alias.get('models', [model['model']])
        # An aggregate coverage row is not evidence of simultaneous variant releases.
        # Browse groups are display vocabulary and safe to share across variants;
        # dates and report associations stay per-variant.
        add(model, names, len(names) == 1 or alias.get('shared_release', False),
            len(names) == 1 or alias.get('shared_reports', False), True)
    return sorted(models.values(), key=lambda m: (not bool(m['release_date']), m['release_date'],
                                                  m['vendor'], m['model'].casefold()))
