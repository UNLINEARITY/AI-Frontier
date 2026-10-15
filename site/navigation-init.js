/* Register before first paint, and again read state when a cached document becomes visible. */
(() => {
  const key = 'ai-frontier-journey';
  let active;
  function pending() {
    let stored;
    try {stored = JSON.parse(sessionStorage.getItem(key));} catch { /* Storage is optional. */ }
    if (stored && stored.to === location.pathname && Date.now() - stored.at < 30000) active = stored;
    return active;
  }
  function restore() {
    const journey = pending();
    if (!journey) return;
    document.documentElement.dataset.journey = journey.kind;
    window.frontierEntry = journey;
    if (journey.kind === 'publishers-return') {
      if (journey.home) history.replaceState(null, '', journey.home);
      const section = document.querySelector('#publishers');
      const y = section ? section.getBoundingClientRect().top + scrollY - document.querySelector('header').offsetHeight - 20 : journey.y || 0;
      for (const tile of document.querySelectorAll('.publisher-grid .publisher-tile')) {
        tile.getAnimations().forEach(animation => animation.cancel());
        tile.style.viewTransitionName = tile.dataset.publisher === journey.publisher ? 'publisher-focus' : 'none';
      }
      scrollTo({top: Math.max(0, y), behavior: 'instant'});
    }
    if (journey.kind === 'home-return') scrollTo({top: journey.y || 0, behavior: 'instant'});
  }
  if (pending()) {document.documentElement.dataset.journey = active.kind; window.frontierEntry = active;}
  addEventListener('pagereveal', event => {
    restore();
    const transition = event.viewTransition;
    if (!transition) return;
    transition.ready.catch(() => {});
    transition.updateCallbackDone?.catch(() => {});
    const clear = () => delete document.documentElement.dataset.journey;
    window.frontierArrival = transition.finished.catch(() => {});
    transition.finished.then(clear, clear);
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) transition.skipTransition();
  });
  addEventListener('pageswap', event => {
    event.viewTransition?.ready.catch(() => {});
    event.viewTransition?.finished.catch(() => {});
    event.viewTransition?.updateCallbackDone?.catch(() => {});
  });
  addEventListener('pageshow', () => {
    restore();
    if (!active) return;
    try {sessionStorage.removeItem(key);} catch { /* Optional. */ }
    setTimeout(() => delete document.documentElement.dataset.journey, 1200);
  });
  addEventListener('pagehide', () => {active = null;});
})();
