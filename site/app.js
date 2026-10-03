const cards = [...document.querySelectorAll('.card')];
const search = document.querySelector('#search');
const vendor = document.querySelector('#vendor');
const type = document.querySelector('#type');
const category = document.querySelector('#category');
const sort = document.querySelector('#sort');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const systemTheme = matchMedia('(prefers-color-scheme: dark)');
const themeMenu = document.querySelector('.theme-menu');
let themePreference = document.documentElement.dataset.themePreference || 'system';
let themeTransition;
function updateThemeControls() {
  for (const button of document.querySelectorAll('[data-theme-choice]')) button.setAttribute('aria-pressed', String(button.dataset.themeChoice === themePreference));
  document.querySelector('meta[name="theme-color"]').content = document.documentElement.dataset.theme === 'dark' ? '#09121e' : '#f6f8fb';
}
function applyTheme(preference, animate = true) {
  themePreference = preference;
  try {localStorage.setItem('ai-frontier-theme', preference);} catch { /* Optional persistence. */ }
  const theme = preference === 'system' ? (systemTheme.matches ? 'dark' : 'light') : preference;
  const update = () => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.themePreference = preference;
    updateThemeControls();
  };
  if (animate && !reducedMotion.matches && document.startViewTransition && document.documentElement.dataset.theme !== theme) {
    themeTransition?.skipTransition();
    themeTransition = document.startViewTransition(update);
    themeTransition.finished.catch(() => {});
  }
  else update();
}
for (const button of document.querySelectorAll('[data-theme-choice]')) button.addEventListener('click', () => {
  themeMenu.open = false;
  applyTheme(button.dataset.themeChoice);
  themeMenu.querySelector('summary').focus({preventScroll: true});
});
addEventListener('storage', event => {
  if (event.key === 'ai-frontier-theme') applyTheme(['system', 'light', 'dark'].includes(event.newValue) ? event.newValue : 'system', false);
});
systemTheme.addEventListener('change', () => {if (themePreference === 'system') applyTheme('system', false);});
document.addEventListener('click', event => {if (!themeMenu.contains(event.target)) themeMenu.open = false;});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && themeMenu.open) {themeMenu.open = false; themeMenu.querySelector('summary').focus();}
});
updateThemeControls();
const grid = document.querySelector('#cards');
let view = 'reports';
let firstRender = true;
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) if (entry.isIntersecting) {
    if (!reducedMotion.matches) entry.target.classList.add('reveal');
    observer.unobserve(entry.target);
  }
}, {threshold: 0.05});
const params = new URLSearchParams(location.search);
function selectValue(element, value) {
  if ([...element.options].some(option => option.value === value)) element.value = value;
}
search.value = params.get('q') || '';
for (const [element, key] of [[vendor, 'publisher'], [type, 'type'], [category, 'category'], [sort, 'sort']]) selectValue(element, params.get(key));
if (params.get('view') === 'models') view = 'models';
function syncView() {
  for (const tab of document.querySelectorAll('[data-tab]')) tab.setAttribute('aria-pressed', String(tab.dataset.tab === view));
  document.querySelector('#type-field').hidden = view !== 'reports';
  document.querySelector('#category-field').hidden = view !== 'models';
  document.querySelector('.sort-field').hidden = view !== 'reports';
}
function filter() {
  const previousPositions = new Map();
  if (!firstRender && !reducedMotion.matches) for (const card of cards) if (!card.hidden) {
    const rect = card.getBoundingClientRect();
    if (rect.bottom > 0 && rect.top < innerHeight) previousPositions.set(card, rect);
  }
  const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  let count = 0;
  for (const card of cards) {
    const visible = card.dataset.view === view &&
      (!vendor.value || card.dataset.vendor === vendor.value) &&
      terms.every(term => card.dataset.search.toLocaleLowerCase().includes(term)) &&
      (view === 'reports' ? !type.value || card.dataset.type === type.value :
        !category.value || card.dataset.category.split(' ').includes(category.value));
    card.hidden = !visible;
    observer.unobserve(card);
    if (visible) {
      count++;
      // Keep existing cards steady while typing; animate newly revealed cards only.
      card.style.setProperty('--stagger', `${Math.min((count - 1) % 3, 2) * 55}ms`);
      observer.observe(card);
    }
  }
  const visible = cards.filter(card => !card.hidden);
  if (view === 'reports') visible.sort((a, b) => {
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
  document.querySelector('#clear').hidden = !search.value && !vendor.value && !(view === 'reports' ? type.value : category.value);
  for (const lab of document.querySelectorAll('[data-publisher]')) lab.setAttribute('aria-pressed', String(lab.dataset.publisher === vendor.value));
  const state = new URLSearchParams();
  if (view === 'models') state.set('view', view);
  for (const [key, value] of [['q', search.value], ['publisher', vendor.value], [view === 'reports' ? 'type' : 'category', view === 'reports' ? type.value : category.value]]) if (value) state.set(key, value);
  if (view === 'reports' && sort.value !== 'newest') state.set('sort', sort.value);
  const suffix = state.size ? `?${state}` : '';
  history.replaceState(null, '', `${location.pathname}${suffix}${location.hash}`);
  const language = document.querySelector('.language-link');
  const target = new URL(language.href);
  target.search = state.toString();
  language.href = target.href;
  if (!firstRender && !reducedMotion.matches) result.animate([{opacity: 0.3, transform: 'translateY(4px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 220});
  firstRender = false;
  scrollFeedback();
}
for (const element of [search, vendor, type, category, sort]) element.addEventListener('input', filter);
for (const button of document.querySelectorAll('[data-tab]')) button.addEventListener('click', () => {
  view = button.dataset.tab;
  syncView();
  filter();
});
function clear() {
  search.value = vendor.value = type.value = category.value = '';
  filter();
  search.focus({preventScroll: true});
}
for (const id of ['#clear', '#empty-clear']) document.querySelector(id).addEventListener('click', clear);
for (const lab of document.querySelectorAll('[data-publisher]')) lab.addEventListener('click', () => {
  vendor.value = vendor.value === lab.dataset.publisher ? '' : lab.dataset.publisher;
  filter();
  document.querySelector('#collection').scrollIntoView({behavior: reducedMotion.matches ? 'instant' : 'smooth', block: 'start'});
});
document.addEventListener('keydown', event => {
  if (event.key === '/' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
    event.preventDefault(); search.focus();
  }
  if (event.key === 'Escape' && document.activeElement === search) {search.value = ''; filter(); search.blur();}
});
let scheduled = false;
function scrollFeedback() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => {
    const height = document.documentElement.scrollHeight - innerHeight;
    document.querySelector('.reading-progress').style.transform = `scaleX(${height > 0 ? scrollY / height : 0})`;
    document.querySelector('#back-top').hidden = scrollY < 700;
    document.querySelector('header').classList.toggle('scrolled', scrollY > 20);
    scheduled = false;
  });
}
addEventListener('scroll', scrollFeedback, {passive: true});
document.querySelector('#back-top').addEventListener('click', () => scrollTo({top: 0, behavior: reducedMotion.matches ? 'instant' : 'smooth'}));
if (matchMedia('(hover: hover)').matches) {
  let pointerFrame = 0;
  grid.addEventListener('pointermove', event => {
    if (pointerFrame || reducedMotion.matches) return;
    const card = event.target.closest('.card');
    if (!card) return;
    pointerFrame = requestAnimationFrame(() => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty('--pointer-x', `${event.clientX - rect.left}px`);
      card.style.setProperty('--pointer-y', `${event.clientY - rect.top}px`);
      pointerFrame = 0;
    });
  });
}
syncView();
filter();
scrollFeedback();
if (!reducedMotion.matches) for (const number of document.querySelectorAll('[data-count]')) {
  const target = Number(number.dataset.count), start = performance.now();
  number.setAttribute('aria-label', String(target));
  function tick(now) {
    const progress = reducedMotion.matches ? 1 : Math.min((now - start) / 850, 1);
    number.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
