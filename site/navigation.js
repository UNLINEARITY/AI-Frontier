/* Native pages, with a saved home position and a deliberate pull back at the reports page top. */
(() => {
  const folder = new URL('.', location.href).pathname;
  const originKey = `ai-frontier-home:${folder}`;
  const journeyKey = 'ai-frontier-journey';
  const write = (key, value) => {try {sessionStorage.setItem(key, JSON.stringify(value));} catch { /* Optional. */ }};
  const read = key => {try {return JSON.parse(sessionStorage.getItem(key));} catch {return null;}};
  const journey = (kind, url, y = 0) => {
    document.documentElement.dataset.journey = kind;
    write(journeyKey, {kind, to: new URL(url, location.href).pathname, y, at: Date.now()});
  };
  if (document.body.dataset.page === 'home') {
    document.addEventListener('click', event => {
      const link = event.target.closest('[data-report-entry]');
      if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      write(originKey, {url: location.href, y: scrollY, at: Date.now()});
      journey('reports-enter', link.href);
    });
    return;
  }
  if (document.body.dataset.page !== 'reports') return;
  const saved = read(originKey);
  let home = new URL('index.html', location.href), position = 0;
  if (saved && Date.now() - saved.at < 86400000) {
    try {
      const url = new URL(saved.url);
      if (url.origin === location.origin && new URL('.', url).pathname === folder && /\/(?:index\.html)?$/.test(url.pathname)) {
        home = url; position = Number.isFinite(saved.y) ? saved.y : 0;
      }
    } catch { /* Use the ordinary home link. */ }
  }
  const link = document.querySelector('[data-report-return]');
  link.href = home.href;
  let returning = false;
  function returnHome() {
    if (returning) return;
    returning = true;
    journey('home-return', home, position);
    const previous = new URL(document.referrer || home.origin);
    const sameHome = previous.origin === home.origin && previous.pathname === home.pathname && previous.search === home.search;
    if (sameHome && document.referrer && history.length > 1) history.back();
    else location.assign(home);
  }
  link.addEventListener('click', event => {
    if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); returnHome();
  });
  let topSince = scrollY <= 1 ? performance.now() : null;
  addEventListener('scroll', () => {
    if (scrollY > 1) topSince = null;
    else if (topSince == null) topSince = performance.now();
  }, {passive: true});
  let distance = 0, lastWheel = 0;
  addEventListener('wheel', event => {
    const now = performance.now();
    if (scrollY > 1 || event.deltaY >= 0 || Math.abs(event.deltaX) > Math.abs(event.deltaY) || event.ctrlKey || event.metaKey || topSince == null || now - topSince < 160) {
      distance = 0; return;
    }
    if (now - lastWheel > 500) distance = 0;
    lastWheel = now;
    distance += -event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? innerHeight : 1);
    if (distance >= 80) returnHome();
  }, {passive: true});
  let touch;
  addEventListener('touchstart', event => {
    touch = event.touches.length === 1 && scrollY <= 1 ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;
  }, {passive: true});
  addEventListener('touchend', event => {
    if (!touch || scrollY > 1 || event.changedTouches.length !== 1) return;
    const end = event.changedTouches[0], dy = end.clientY - touch.y, dx = end.clientX - touch.x;
    touch = null;
    if (dy >= 90 && dy > Math.abs(dx) * 1.3) returnHome();
  }, {passive: true});
  addEventListener('touchcancel', () => {touch = null;}, {passive: true});
  addEventListener('pageshow', () => {
    returning = false; distance = 0; lastWheel = 0; touch = null;
    topSince = scrollY <= 1 ? performance.now() : null;
  });
})();
