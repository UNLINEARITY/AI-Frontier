const viewer = document.querySelector('.image-viewer');
const viewerImage = document.querySelector('#viewer-image');
let opener;
for (const button of document.querySelectorAll('[data-preview]')) button.addEventListener('click', event => {
  event.preventDefault();
  opener = button;
  viewerImage.src = button.dataset.preview;
  viewerImage.alt = button.querySelector('img').alt;
  document.querySelector('#viewer-title').textContent = button.dataset.title;
  viewerImage.classList.remove('actual-size');
  viewer.showModal();
  document.body.style.overflow = 'hidden';
});
viewerImage.addEventListener('click', () => viewerImage.classList.toggle('actual-size'));
document.querySelector('.viewer-close').addEventListener('click', () => viewer.close());
viewer.addEventListener('click', event => {if (event.target === viewer) viewer.close();});
viewer.addEventListener('close', () => {
  document.body.style.overflow = '';
  opener?.focus({preventScroll: true});
});
// Preserve the selected figure when switching languages.
const language = document.querySelector('.language-link');
language.addEventListener('click', () => {language.hash = location.hash;});

// Timeline paging: the build writes both neighbours, these handlers pick the direction.
const journeyKey = 'ai-frontier-journey';
const pager = document.querySelector('.reader-pager');
const previousLink = document.querySelector('.reader-pager-link--prev');
const nextLink = document.querySelector('.reader-pager-link--next');
let navigating = false;

function remember(direction, href) {
  try {
    sessionStorage.setItem(journeyKey, JSON.stringify({kind: `reader-${direction}`, to: new URL(href).pathname, at: Date.now()}));
  } catch { /* Storage is optional. */ }
}

function follow(direction) {
  const link = direction === 'prev' ? previousLink : nextLink;
  if (!link || navigating) return;
  navigating = true;
  remember(direction, link.href);
  location.href = link.href;
}

for (const link of document.querySelectorAll('.reader-tool--step, .reader-pager-link')) {
  link.addEventListener('click', event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    remember(link.rel === 'prev' ? 'prev' : 'next', link.href);
  });
}

function readerIsBusy() {
  return document.querySelector('dialog[open]') !== null || document.documentElement.classList.contains('textfold-lightbox-open');
}

function pagingShouldYield(target) {
  return target instanceof Element && Boolean(target.closest(
    '[data-textfold-inline], iframe, table, input, textarea, select, button, a, [contenteditable="true"], [data-paging-ignore]'
  ));
}

addEventListener('keydown', event => {
  if (!pager || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
  if (readerIsBusy()) return;
  const target = event.target;
  if (pagingShouldYield(target)) return;
  event.preventDefault();
  follow(event.key === 'ArrowLeft' ? 'prev' : 'next');
});

// Touch: a horizontal drag turns the page. Vertical scrolling keeps its own gesture.
let touchStart;
addEventListener('touchstart', event => {
  if (!pager || readerIsBusy() || event.touches.length !== 1 || pagingShouldYield(event.target)) return;
  const point = event.touches[0];
  touchStart = {x: point.clientX, y: point.clientY};
}, {passive: true});
addEventListener('touchend', event => {
  if (!touchStart) return;
  const point = event.changedTouches[0];
  const dx = (point?.clientX ?? touchStart.x) - touchStart.x;
  const dy = (point?.clientY ?? touchStart.y) - touchStart.y;
  touchStart = undefined;
  if (Math.abs(dx) < 64 || Math.abs(dx) < Math.abs(dy) * 1.6) return;
  follow(dx < 0 ? 'next' : 'prev');
}, {passive: true});
addEventListener('touchcancel', () => {touchStart = undefined;}, {passive: true});

// Trackpad: two-finger horizontal scroll turns the page once per gesture.
let horizontal = 0;
let wheelTimer;
addEventListener('wheel', event => {
  if (!pager || event.ctrlKey || readerIsBusy() || pagingShouldYield(event.target)) return;
  if (Math.abs(event.deltaX) <= Math.abs(event.deltaY) * 1.2) {horizontal = 0; return;}
  horizontal += event.deltaX;
  clearTimeout(wheelTimer);
  wheelTimer = setTimeout(() => {horizontal = 0;}, 240);
  if (Math.abs(horizontal) > 80) {
    const direction = horizontal > 0 ? 'next' : 'prev';
    horizontal = 0;
    follow(direction);
  }
}, {passive: true});

// "Home" is always the unfiltered home page. Coming straight from it, step back so
// the reader lands where they left; from anywhere else, open the home page itself.
for (const homeLink of document.querySelectorAll('[data-reader-home]')) homeLink.addEventListener('click', event => {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  try {
    const from = new URL(document.referrer), home = new URL(homeLink.href);
    const page = url => url.pathname.replace(/index\.html$/, '');
    if (from.origin === home.origin && page(from) === page(home) && !from.search && history.length > 1) {
      event.preventDefault();
      history.back();
    }
  } catch { /* No usable referrer: follow the link. */ }
});

// One bottom bar: TextFold's detail control is drawn in a fixed layer above this bar,
// so the bar leaves a slot of its width in the middle. Use the first layout that fits:
// one row, then two rows inside the same bar (control on top).
const toolbar = document.querySelector('.reader-toolbar');
if (toolbar) {
  const bar = toolbar.querySelector('.reader-toolbar-bar');
  const foldBar = () => document.querySelector('[data-textfold-inline]')?.shadowRoot?.querySelector('.zoombar');
  let frame = 0;
  function fitToolbar() {
    frame = 0;
    // The slot already has the control's width: a still copy holds it from the first frame.
    const room = document.documentElement.clientWidth - 24;
    for (const mode of ['row', 'stacked']) {
      toolbar.dataset.mode = mode;
      if (mode === 'stacked' || bar.getBoundingClientRect().width <= room) break;
    }
    // Stacked: the control rises by one row (36px) plus the row gap (2px) to sit in the top row.
    document.documentElement.style.setProperty('--reader-toolbar-lift', toolbar.dataset.mode === 'stacked' ? '38px' : '0px');
  }
  const schedule = () => {if (!frame) frame = requestAnimationFrame(fitToolbar);};
  addEventListener('resize', schedule);
  addEventListener('ai-frontier-reader-ready', () => {
    toolbar.dataset.foldReady = '';
    schedule();
    const fold = foldBar();
    if (fold) new ResizeObserver(schedule).observe(fold);
  });
  fitToolbar();
}
