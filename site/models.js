/* One filter state owns the timeline and every model row. Zoom changes the list as well. */
(() => {
  const rows = [...document.querySelectorAll('.model-row')];
  const search = document.querySelector('#search'), publisher = document.querySelector('#vendor');
  const category = document.querySelector('#category'), scope = document.querySelector('#scope'), sort = document.querySelector('#sort');
  const grid = document.querySelector('#cards'), clear = document.querySelector('#clear'), result = document.querySelector('#result-count');
  const focus = document.querySelector('#publisher-focus'), choices = document.querySelector('#publisher-choices').content;
  const params = new URLSearchParams(location.search);
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase().replaceAll('π', 'pi').replace(/[^\p{L}\p{N}]/gu, '');
  search.value = params.get('q') || params.get('model') || '';
  for (const [element, key] of [[publisher, 'publisher'], [category, 'category'], [scope, 'scope'], [sort, 'sort']]) {
    if ([...element.options].some(option => option.value === params.get(key))) element.value = params.get(key);
  }
  let terms = [], windowRange = null, lastSort = '', displayedPublisher;
  const from = Date.parse(params.get('from')), to = Date.parse(params.get('to'));
  if (Number.isFinite(from) && Number.isFinite(to) && from < to) windowRange = {from, to, full: false};
  const searchText = model => normalize(`${model.model} ${model.vendor} ${model.publisher_en} ${model.publisher_cn} ${(model.aliases || []).join(' ')}`);
  const termsByModel = new Map(JSON.parse(document.querySelector('#timeline-data').textContent).map(model => [`${model.vendor}\0${model.model}`, searchText(model)]));
  for (const row of rows) row.searchTerms = termsByModel.get(`${row.dataset.vendor}\0${row.dataset.title}`) || normalize(row.dataset.search);
  function matches(model, ignorePublisher = false) {
    return (ignorePublisher || !publisher.value || model.vendor === publisher.value) &&
      (!category.value || model.categories.includes(category.value)) &&
      (scope.value !== 'frontier' || model.frontier) && (scope.value !== 'undated' || !model.release_date) &&
      terms.every(term => model.searchTerms.includes(term));
  }
  function renderFocus() {
    if (displayedPublisher === publisher.value) return;
    displayedPublisher = publisher.value;
    const source = [...choices.querySelectorAll('[data-publisher]')].find(tile => tile.dataset.publisher === publisher.value);
    const tile = document.createElement('div');
    tile.className = source.className; tile.innerHTML = source.innerHTML;
    tile.dataset.publisher = publisher.value; tile.style.viewTransitionName = 'publisher-focus';
    tile.classList.add('publisher-tile--focus');
    const name = tile.querySelector('.tile-name'), heading = document.createElement('h1');
    heading.className = 'tile-name'; heading.textContent = name.textContent; name.replaceWith(heading);
    focus.replaceChildren(tile);
    document.title = `${publisher.value ? heading.textContent + ' — ' : ''}${focus.dataset.pageTitle}`;
  }
  function filterRows() {
    let count = 0;
    if (lastSort !== sort.value) {
      rows.sort((a, b) => {
        if (sort.value === 'title') return a.dataset.title.localeCompare(b.dataset.title);
        if (!a.dataset.date || !b.dataset.date) return Number(!a.dataset.date) - Number(!b.dataset.date) || a.dataset.title.localeCompare(b.dataset.title);
        return sort.value === 'oldest' ? a.dataset.date.localeCompare(b.dataset.date) : b.dataset.date.localeCompare(a.dataset.date);
      });
      rows.forEach(row => grid.append(row)); lastSort = sort.value;
    }
    for (const row of rows) {
      const model = {vendor: row.dataset.vendor, categories: row.dataset.category.split(' '), frontier: row.dataset.frontier === '1', release_date: row.dataset.date, searchTerms: row.searchTerms};
      const time = Date.parse(model.release_date + 'T00:00:00Z');
      const inWindow = !windowRange || windowRange.full || (Number.isFinite(time) && time >= windowRange.from && time <= windowRange.to);
      const visible = matches(model) && inWindow;
      if (row.hidden === visible) row.hidden = !visible;
      if (visible) {count++; window.frontierMotion?.observe(row, 'row');}
    }
    result.textContent = `${count} ${result.dataset.label}`;
    document.querySelector('#empty').hidden = count !== 0;
    clear.hidden = !search.value && !publisher.value && !category.value && scope.value === 'all' && (!windowRange || windowRange.full);
  }
  function persistWindow(from, to, full) {
    const state = new URLSearchParams();
    for (const [key, value] of [['q', search.value.trim()], ['publisher', publisher.value], ['category', category.value]]) if (value) state.set(key, value);
    if (scope.value !== 'all') state.set('scope', scope.value);
    if (sort.value !== 'newest') state.set('sort', sort.value);
    if (!full && Number.isFinite(from) && Number.isFinite(to)) {state.set('from', new Date(from).toISOString()); state.set('to', new Date(to).toISOString());}
    const suffix = state.size ? `?${state}` : '';
    history.replaceState(null, '', `${location.pathname}${suffix}${location.hash}`);
    const language = new URL(document.querySelector('.language-link').href);
    language.search = state.toString(); language.hash = location.hash; document.querySelector('.language-link').href = language.href;
    for (const link of document.querySelectorAll('[data-report-entry]')) {
      const url = new URL(link.href); publisher.value ? url.searchParams.set('publisher', publisher.value) : url.searchParams.delete('publisher'); link.href = url.href;
    }
  }
  function filter(event) {
    const publisherChanged = displayedPublisher !== publisher.value;
    terms = search.value.trim().split(/\s+/).map(normalize).filter(Boolean);
    renderFocus(); filterRows();
    persistWindow(windowRange?.from, windowRange?.to, windowRange?.full ?? true);
    if (event) document.dispatchEvent(new CustomEvent('frontier:filters', {detail: {publisherChanged, fit: event.target !== sort}}));
  }
  window.frontierModels = {matches, searchText, publisher: () => publisher.value, persistWindow,
    setWindow(from, to, full) {windowRange = {from, to, full}; filterRows();}};
  for (const control of [search, publisher, category, scope, sort]) control.addEventListener('input', filter);
  function reset() {
    search.value = publisher.value = category.value = ''; scope.value = 'all'; windowRange = null;
    filter({target: scope}); search.focus({preventScroll: true});
  }
  clear.addEventListener('click', reset); document.querySelector('#empty-clear').addEventListener('click', reset);
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {event.preventDefault(); search.focus();}
    if (event.key === 'Escape' && document.activeElement === search) {search.value = ''; filter({target: search}); search.blur();}
  });
  filter();
})();
