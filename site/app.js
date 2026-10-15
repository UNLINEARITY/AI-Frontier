/* The homepage is an overview; the complete collections have their own routes. */
(() => {
  const tiles = [...document.querySelectorAll('.publisher-tile')];
  const params = new URLSearchParams(location.search);
  const legacyModels = params.get('view') === 'models';
  const legacyReports = params.has('q') || params.has('type') || params.has('sort') || location.hash === '#collection';
  if (legacyModels || legacyReports) {
    const destination = new URL(legacyModels ? 'models.html' : 'reports.html', location.href);
    destination.search = params.toString(); destination.searchParams.delete('view'); destination.hash = 'collection';
    if (legacyModels) {destination.searchParams.delete('type'); destination.searchParams.set('scope', 'frontier');}
    location.replace(destination.href);
  }
  let publisher = params.get('publisher') || '';
  if (!tiles.some(tile => tile.dataset.publisher === publisher)) publisher = '';
  function select(value, reset = false) {
    publisher = value;
    for (const tile of tiles) tile.setAttribute('aria-pressed', String(tile.dataset.publisher === publisher));
    const label = document.querySelector('#publisher-selection');
    label.textContent = publisher ? tiles.find(tile => tile.dataset.publisher === publisher).dataset.label : '';
    const state = new URLSearchParams(location.search);
    if (publisher) state.set('publisher', publisher); else state.delete('publisher');
    if (reset) for (const key of ['model', 'from', 'to']) state.delete(key);
    history.replaceState(null, '', `${location.pathname}${state.size ? `?${state}` : ''}${location.hash}`);
    for (const entry of document.querySelectorAll('[data-report-entry], [data-model-entry]')) {
      const destination = new URL(entry.href);
      if (publisher) destination.searchParams.set('publisher', publisher); else destination.searchParams.delete('publisher');
      entry.href = destination.href;
    }
    const language = new URL(document.querySelector('.language-link').href);
    language.search = state.toString(); language.hash = location.hash;
    document.querySelector('.language-link').href = language.href;
    document.dispatchEvent(new CustomEvent('frontier:publisher', {detail: publisher}));
    if (reset) document.dispatchEvent(new Event('frontier:reset'));
  }
  for (const tile of tiles) tile.addEventListener('click', () => {
    const value = tile.dataset.publisher;
    select(value === publisher ? '' : value, !value);
  });
  document.addEventListener('keydown', event => {
    const input = document.querySelector('#timeline-search');
    if (event.key === '/' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
      event.preventDefault(); input.focus();
    }
    if (event.key === 'Escape' && document.activeElement === input) {input.value = ''; input.dispatchEvent(new Event('input')); input.blur();}
  });
  select(publisher);
})();
