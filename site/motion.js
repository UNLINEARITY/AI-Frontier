/* Scroll owns progress. Each unit exposes --p (0 → 1 while it enters) and the page
   exposes --x on the masthead/hero (0 → 1 while the top scrolls away). CSS decides
   what each kind of content does with that progress, in both scroll directions.
   Document positions are cached, so a scroll frame only reads scrollY and writes
   changed values. Without JS or with reduced motion, --p stays 1: content is still. */
(() => {
  const root = document.documentElement;
  const units = [];
  const kinds = [
    ['.section-heading', 'heading', .38],
    ['.publisher-grid', 'tiles', .5],
    ['.timeline-section', 'timeline', .55],
    ['.stats', 'stats', .5],
    ['.proof-table', 'rows', .45],
    ['.showcase', 'showcase', .5],
    ['.cta', 'band', .45],
    ['.footer-inner', 'footer', .3],
    ['.directory-heading', 'heading', .3],
    ['.collection-header', 'heading', .3]
  ];
  let positions = [], height = innerHeight, maximum = 0, frame = 0, measured = false;
  const counters = [...document.querySelectorAll('[data-count]')];

  function register(element, kind, travel) {
    if (units.some(unit => unit.element === element)) return;
    element.dataset.m = kind;
    // Children receive their order so CSS can stagger them without inline styles.
    const parts = kind === 'tiles' ? element.children : kind === 'rows' ? element.querySelectorAll('tbody tr')
      : kind === 'stats' ? element.querySelectorAll('.ui-plot rect') : [];
    [...parts].forEach((part, index) => {part.style.setProperty('--i', index); part.style.setProperty('--n', parts.length);});
    if (kind === 'tiles') {
      const columns = () => getComputedStyle(element).gridTemplateColumns.split(' ').length;
      element.motionColumns = columns;
    }
    units.push({element, kind, travel, last: -1});
  }
  for (const [selector, kind, travel] of kinds) for (const element of document.querySelectorAll(selector)) register(element, kind, travel);

  function stagger() {
    for (const unit of units) {
      if (unit.kind !== 'tiles') continue;
      const columns = Math.max(1, unit.element.motionColumns());
      [...unit.element.children].forEach((tile, index) => {
        const column = index % columns, row = Math.floor(index / columns);
        tile.style.setProperty('--d', Math.min(.55, column * .045 + row * .085).toFixed(3));
      });
    }
  }
  function measure() {
    height = innerHeight; maximum = Math.max(0, root.scrollHeight - height);
    positions = units.map(unit => {
      const bounds = unit.element.getBoundingClientRect();
      const top = bounds.top + scrollY;
      // Progress runs from "top reaches the bottom edge" to "top has travelled
      // a share of the viewport", but never past where the page can scroll.
      const start = top - height, wanted = top - height * (1 - unit.travel);
      const end = Math.max(start + 1, Math.min(wanted, maximum));
      return {start, end};
    });
    stagger(); measured = true;
  }
  function write(element, name, value) {
    const text = value.toFixed(3);
    if (element.style.getPropertyValue(name) !== text) element.style.setProperty(name, text);
  }
  function update() {
    frame = 0;
    if (reducedMotion.matches) return;
    if (!measured) measure();
    const y = scrollY;
    units.forEach((unit, index) => {
      const {start, end} = positions[index];
      const progress = Math.max(0, Math.min(1, (y - start) / (end - start)));
      if (Math.abs(progress - unit.last) < .001) return;
      unit.last = progress; write(unit.element, '--p', progress);
      if (unit.kind === 'stats' && progress > .55) countOnce();
    });
    write(root, '--x', Math.max(0, Math.min(1, y / (height * .75))));
  }
  function schedule() {if (!frame) frame = requestAnimationFrame(update);}
  function remeasure() {measured = false; for (const unit of units) unit.last = -1; schedule();}

  // Numbers jump once, then keep their real value; aria-label always carries it.
  let counted = false;
  function countOnce() {
    if (counted) return;
    counted = true;
    for (const number of counters) {
      const value = Number(number.dataset.count), began = performance.now();
      number.setAttribute('aria-label', String(value));
      const tick = now => {
        const t = Math.min(1, (now - began) / 900), eased = 1 - Math.pow(1 - t, 4);
        number.textContent = String(Math.round(value * eased));
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }
  }

  function enable() {
    if (reducedMotion.matches) {
      root.classList.remove('motion');
      for (const unit of units) unit.element.style.removeProperty('--p');
      root.style.removeProperty('--x');
      for (const number of counters) number.textContent = number.dataset.count;
      return;
    }
    root.classList.add('motion');
    if (!counted) for (const number of counters) {number.setAttribute('aria-label', number.dataset.count); number.textContent = '0';}
    remeasure();
  }
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', remeasure);
  addEventListener('load', remeasure);
  addEventListener('pageshow', remeasure);
  new ResizeObserver(remeasure).observe(document.body);
  reducedMotion.addEventListener('change', enable);
  enable();
  // Lists filter in place; their rows are content to scan, so they do not animate.
  window.frontierMotion = {observe() {}, refresh: remeasure};

  // Section links in the home navigation follow the reading position.
  const pageLink = document.querySelector(`[data-page-link="${document.body.dataset.page}"]`);
  if (pageLink) pageLink.setAttribute('aria-current', 'page');
  if (document.body.dataset.page !== 'home') return;
  const links = [...document.querySelectorAll('.site-nav [data-section]')];
  let navigationFrame = 0;
  function updateNavigation() {
    if (navigationFrame) return;
    navigationFrame = requestAnimationFrame(() => {
      const line = document.querySelector('header').offsetHeight + innerHeight * .3;
      for (const link of links) {
        const bounds = document.getElementById(link.dataset.section)?.getBoundingClientRect();
        if (bounds && bounds.top <= line && bounds.bottom > line) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
      navigationFrame = 0;
    });
  }
  addEventListener('scroll', updateNavigation, {passive: true}); addEventListener('resize', updateNavigation); updateNavigation();
})();
