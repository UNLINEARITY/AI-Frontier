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
    if (journey.kind === 'home-return') scrollTo({top: journey.y || 0, behavior: 'instant'});
  }
  if (pending()) document.documentElement.dataset.journey = active.kind;
  addEventListener('pagereveal', event => {
    restore();
    const transition = event.viewTransition;
    if (!transition) return;
    transition.ready.catch(() => {});
    transition.updateCallbackDone?.catch(() => {});
    const clear = () => delete document.documentElement.dataset.journey;
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
