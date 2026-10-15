const cards = [...document.querySelectorAll('.card')];
const search = document.querySelector('#search');
const vendor = document.querySelector('#vendor');
const type = document.querySelector('#type');
const sort = document.querySelector('#sort');
const grid = document.querySelector('#cards');
let firstRender = true;
const params = new URLSearchParams(location.search);
if (params.get('view') === 'models') {
  const destination = new URL('models.html', location.href);
  destination.search = params.toString();
  destination.searchParams.delete('view'); destination.searchParams.delete('type');
  destination.searchParams.set('scope', 'frontier'); destination.hash = 'collection';
  location.replace(destination.href);
}
function selectValue(element, value) {
  if ([...element.options].some(option => option.value === value)) element.value = value;
}
search.value = params.get('q') || '';
for (const [element, key] of [[vendor, 'publisher'], [type, 'type'], [sort, 'sort']]) selectValue(element, params.get(key));
function filter() {
  const previousPositions = new Map();
  if (!firstRender && !reducedMotion.matches) for (const card of cards) if (!card.hidden) {
    const rect = card.getBoundingClientRect();
    if (rect.bottom > 0 && rect.top < innerHeight) previousPositions.set(card, rect);
  }
  const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  let count = 0;
  for (const card of cards) {
    const visible = (!vendor.value || card.dataset.vendor === vendor.value) &&
      terms.every(term => card.dataset.search.toLocaleLowerCase().includes(term)) &&
      (!type.value || card.dataset.type === type.value);
    card.hidden = !visible;
    if (visible) {
      count++;
      window.frontierMotion?.observe(card, 'row');
    }
  }
  const visible = cards.filter(card => !card.hidden);
  visible.sort((a, b) => {
    if (sort.value === 'title') return a.dataset.title.localeCompare(b.dataset.title);
    if (!a.dataset.date || !b.dataset.date) return Number(!a.dataset.date) - Number(!b.dataset.date);
    return sort.value === 'oldest' ? a.dataset.date.localeCompare(b.dataset.date) : b.dataset.date.localeCompare(a.dataset.date);
  });
  for (const card of visible) grid.append(card);
  for (const [card, previous] of previousPositions) if (!card.hidden) {
    const next = card.getBoundingClientRect();
    const x = previous.left - next.left, y = previous.top - next.top;
    if ((x || y) && next.top < innerHeight && next.bottom > 0) {
      card.getAnimations().forEach(animation => animation.cancel());
      card.animate([{translate: `${x}px ${y}px`}, {translate: '0 0'}], {duration: 280, easing: 'cubic-bezier(.2,.8,.2,1)'});
    }
  }
  const result = document.querySelector('#result-count');
  result.textContent = `${count} ${result.dataset.label}`;
  document.querySelector('#empty').hidden = count !== 0;
  document.querySelector('#clear').hidden = !search.value && !vendor.value && !type.value;
  const state = new URLSearchParams();
  for (const [key, value] of [['q', search.value], ['publisher', vendor.value], ['type', type.value]]) if (value) state.set(key, value);
  if (sort.value !== 'newest') state.set('sort', sort.value);
  const suffix = state.size ? `?${state}` : '';
  history.replaceState(null, '', `${location.pathname}${suffix}${location.hash}`);
  const language = document.querySelector('.language-link');
  const target = new URL(language.href);
  target.search = state.toString();
  target.hash = location.hash;
  language.href = target.href;
  if (!firstRender && !reducedMotion.matches) result.animate([{opacity: 0.3, transform: 'translateY(4px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 220});
  firstRender = false;
  for (const entry of document.querySelectorAll('[data-model-entry]')) {
    const destination = new URL(entry.href);
    if (vendor.value) destination.searchParams.set('publisher', vendor.value); else destination.searchParams.delete('publisher');
    entry.href = destination.href;
  }
  scrollFeedback();
}
for (const element of [search, vendor, type, sort]) element.addEventListener('input', filter);
function clear() {
  search.value = vendor.value = type.value = '';
  filter();
  search.focus({preventScroll: true});
}
for (const id of ['#clear', '#empty-clear']) document.querySelector(id).addEventListener('click', clear);
document.addEventListener('keydown', event => {
  if (event.key === '/' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
    event.preventDefault();
    const timeline = document.querySelector('#timeline');
    const bounds = timeline?.getBoundingClientRect();
    (bounds && bounds.top < innerHeight && bounds.bottom > 0 ? document.querySelector('#timeline-search') : search).focus();
  }
  if (event.key === 'Escape' && document.activeElement === search) {search.value = ''; filter(); search.blur();}
});
filter();
scrollFeedback();
