/* The lab index is a set of direct entrances; the complete explorer lives on Models. */
(() => {
  const params = new URLSearchParams(location.search);
  if (params.get('view') === 'models' || params.has('model') || params.has('from') || location.hash === '#timeline') {
    const destination = new URL('models.html', location.href);
    destination.search = params.toString(); destination.searchParams.delete('view');
    if (params.get('view') === 'models') destination.searchParams.set('scope', 'frontier');
    destination.hash = location.hash === '#timeline' ? 'timeline' : '';
    location.replace(destination);
  } else if (params.has('q') || params.has('type') || params.has('sort') || location.hash === '#collection') {
    const destination = new URL('reports.html', location.href);
    destination.search = params.toString(); location.replace(destination);
  }
  const tiles = [...document.querySelectorAll('.publisher-grid .publisher-tile')];
  const grid = document.querySelector('.publisher-grid');
  let departing = false, abandoned = false, departure = 0;
  addEventListener('pagehide', () => {abandoned = true; departure++;});
  function reset() {
    departure++; departing = false; abandoned = false; grid.removeAttribute('aria-busy');
    for (const tile of tiles) {
      tile.getAnimations().forEach(animation => animation.cancel());
      if (window.frontierEntry?.kind === 'publishers-return' && tile.dataset.publisher === window.frontierEntry.publisher) tile.style.viewTransitionName = 'publisher-focus';
      else tile.style.removeProperty('view-transition-name');
      tile.removeAttribute('aria-current');
    }
  }
  addEventListener('pageshow', reset);
  document.addEventListener('click', async event => {
    const tile = event.target.closest('.publisher-grid .publisher-tile');
    if (!tile || event.defaultPrevented || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (departing) return;
    const generation = ++departure;
    departing = true; grid.setAttribute('aria-busy', 'true');
    for (const other of tiles) other.style.removeProperty('view-transition-name');
    tile.setAttribute('aria-current', 'true'); tile.style.viewTransitionName = 'publisher-focus';
    window.frontierNavigation?.rememberModels(tile);
    if (!reducedMotion.matches) {
      const selected = tile.getBoundingClientRect();
      const animations = tiles.filter(other => other !== tile).map(other => {
        const bounds = other.getBoundingClientRect();
        const distance = Math.abs(bounds.x - selected.x) + Math.abs(bounds.y - selected.y);
        return other.animate([{opacity: 1, transform: 'none'}, {opacity: 0, transform: 'translateY(12px) scale(.96)'}],
          {duration: 240, delay: Math.min(100, distance / 18), easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'forwards'});
      });
      await Promise.allSettled(animations.map(animation => animation.finished));
    }
    if (!abandoned && generation === departure) location.assign(tile.href);
  });
})();
