/* Direct pages share a lab transition and a deliberate pull back at their top. */
(() => {
  const folder = new URL('.', location.href).pathname;
  const page = document.body.dataset.page;
  const journeyKey = 'ai-frontier-journey';
  const originKey = kind => `ai-frontier-${kind}-home:${folder}`;
  const write = (key, value) => {try {sessionStorage.setItem(key, JSON.stringify(value));} catch { /* Optional. */ }};
  const read = key => {try {return JSON.parse(sessionStorage.getItem(key));} catch {return null;}};
  const journey = (kind, url, extra = {}) => {
    document.documentElement.dataset.journey = kind;
    write(journeyKey, {kind, to: new URL(url, location.href).pathname, at: Date.now(), ...extra});
  };
  function rememberModels(link) {
    const home = new URL(location.href); home.search = ''; home.hash = 'publishers';
    const section = document.querySelector('#publishers');
    const y = Math.max(0, section.getBoundingClientRect().top + scrollY - document.querySelector('header').offsetHeight - 20);
    const publisher = link.dataset.publisher || '';
    write(originKey('models'), {url: home.href, y, publisher, at: Date.now()});
    journey('models-enter', link.href, {publisher});
  }
  window.frontierNavigation = {rememberModels};
  if (page === 'home') {
    document.addEventListener('click', event => {
      const link = event.target.closest('[data-report-entry], [data-model-entry]');
      if (!link || event.defaultPrevented || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (link.hasAttribute('data-model-entry')) {rememberModels(link); return;}
      write(originKey('reports'), {url: location.href, y: scrollY, at: Date.now()});
      journey('reports-enter', link.href);
    });
    return;
  }
  if (page !== 'reports' && page !== 'models') return;
  const saved = read(originKey(page));
  let home = new URL(page === 'models' ? 'index.html#publishers' : 'index.html', location.href), position = 0;
  if (saved && Date.now() - saved.at < 86400000) {
    try {
      const url = new URL(saved.url);
      if (url.origin === location.origin && new URL('.', url).pathname === folder && /\/(?:index\.html)?$/.test(url.pathname)) {home = url; position = Number.isFinite(saved.y) ? saved.y : 0;}
    } catch { /* Ordinary homepage link. */ }
  }
  const links = [...document.querySelectorAll(page === 'models' ? '[data-publisher-return]' : '[data-report-return]')];
  for (const link of links) link.href = home.href;
  let returning = false;
  async function returnHome() {
    if (returning) return;
    returning = true;
    if (page === 'models') await window.frontierTimeline?.returnToPublishers();
    journey(page === 'models' ? 'publishers-return' : 'home-return', home, {y: position, home: home.href, publisher: page === 'models' ? document.querySelector('#vendor').value : saved?.publisher || ''});
    const previous = new URL(document.referrer || home.origin);
    if (document.referrer && previous.origin === home.origin && previous.pathname === home.pathname && previous.search === home.search && history.length > 1) history.back();
    else location.assign(home);
  }
  for (const link of links) link.addEventListener('click', event => {
    if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); returnHome();
  });
  let topSince = scrollY <= 1 ? performance.now() : null, distance = 0, lastWheel = 0, touch;
  addEventListener('scroll', () => {if (scrollY > 1) topSince = null; else if (topSince == null) topSince = performance.now();}, {passive: true});
  addEventListener('wheel', event => {
    const now = performance.now();
    if (scrollY > 1 || event.deltaY >= 0 || Math.abs(event.deltaX) > Math.abs(event.deltaY) || event.ctrlKey || event.metaKey || topSince == null || now - topSince < 160) {distance = 0; return;}
    if (now - lastWheel > 500) distance = 0;
    lastWheel = now; distance += -event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? innerHeight : 1);
    if (distance >= 80) returnHome();
  }, {passive: true});
  addEventListener('touchstart', event => {touch = event.touches.length === 1 && scrollY <= 1 ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;}, {passive: true});
  addEventListener('touchend', event => {
    if (!touch || scrollY > 1 || event.changedTouches.length !== 1) return;
    const end = event.changedTouches[0], dy = end.clientY - touch.y, dx = end.clientX - touch.x; touch = null;
    if (dy >= 90 && dy > Math.abs(dx) * 1.3) returnHome();
  }, {passive: true});
  addEventListener('touchcancel', () => {touch = null;}, {passive: true});
  addEventListener('pageshow', () => {returning = false; distance = 0; lastWheel = 0; touch = null; topSince = scrollY <= 1 ? performance.now() : null;});
})();
