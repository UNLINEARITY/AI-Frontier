/* The complete model directory shares the canonical timeline identities. */
(() => {
  const rows = [...document.querySelectorAll('.model-row')];
  const search = document.querySelector('#search');
  const publisher = document.querySelector('#vendor');
  const category = document.querySelector('#category');
  const scope = document.querySelector('#scope');
  const sort = document.querySelector('#sort');
  const grid = document.querySelector('#cards');
  const clear = document.querySelector('#clear');
  const result = document.querySelector('#result-count');
  const params = new URLSearchParams(location.search);
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase().replaceAll('π', 'pi').replace(/[^\p{L}\p{N}]/gu, '');
  search.value = params.get('q') || params.get('model') || '';
  for (const [element, key] of [[publisher, 'publisher'], [category, 'category'], [scope, 'scope'], [sort, 'sort']]) {
    const value = params.get(key);
    if ([...element.options].some(option => option.value === value)) element.value = value;
  }
  for (const row of rows) row.searchTerms = normalize(row.dataset.search);

  function filter() {
    const terms = search.value.trim().split(/\s+/).map(normalize).filter(Boolean);
    const visible = [];
    for (const row of rows) {
      row.hidden = !((!publisher.value || row.dataset.vendor === publisher.value) &&
        (!category.value || row.dataset.category.split(' ').includes(category.value)) &&
        (scope.value !== 'frontier' || row.dataset.frontier === '1') &&
        (scope.value !== 'undated' || !row.dataset.date) && terms.every(term => row.searchTerms.includes(term)));
      if (!row.hidden) visible.push(row);
    }
    visible.sort((a, b) => {
      if (sort.value === 'title') return a.dataset.title.localeCompare(b.dataset.title);
      if (!a.dataset.date || !b.dataset.date) return Number(!a.dataset.date) - Number(!b.dataset.date) || a.dataset.title.localeCompare(b.dataset.title);
      return sort.value === 'oldest' ? a.dataset.date.localeCompare(b.dataset.date) : b.dataset.date.localeCompare(a.dataset.date);
    });
    visible.forEach((row, index) => {
      grid.append(row);
      row.style.setProperty('--stagger', `${index % 3 * 55}ms`);
      window.frontierMotion?.observe(row, 'row');
    });
    result.textContent = `${visible.length} ${result.dataset.label}`;
    document.querySelector('#empty').hidden = visible.length !== 0;
    clear.hidden = !search.value && !publisher.value && !category.value && scope.value === 'all';
    const state = new URLSearchParams();
    for (const [key, value] of [['q', search.value.trim()], ['publisher', publisher.value], ['category', category.value]]) if (value) state.set(key, value);
    if (scope.value !== 'all') state.set('scope', scope.value);
    if (sort.value !== 'newest') state.set('sort', sort.value);
    history.replaceState(null, '', `${location.pathname}${state.size ? `?${state}` : ''}${location.hash}`);
    const language = new URL(document.querySelector('.language-link').href);
    language.search = state.toString(); language.hash = location.hash;
    document.querySelector('.language-link').href = language.href;
  }
  for (const element of [search, publisher, category, scope, sort]) element.addEventListener('input', filter);
  function reset() {
    search.value = publisher.value = category.value = '';
    scope.value = 'all';
    filter(); search.focus({preventScroll: true});
  }
  clear.addEventListener('click', reset);
  document.querySelector('#empty-clear').addEventListener('click', reset);
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
      event.preventDefault(); search.focus();
    }
    if (event.key === 'Escape' && document.activeElement === search) {search.value = ''; filter(); search.blur();}
  });
  filter();
})();
