/* Each real content block owns its scroll timeline; its background always remains visible. */
(() => {
  const units = new Set();
  const scrollDriven = CSS.supports('animation-timeline: view()');
  const fallbackParts = new Map();
  function observe(element, kind = element.dataset.motion || 'rise') {
    const boundary = kind === 'headline' ? element.parentElement : element;
    if (units.has(boundary)) return;
    units.add(boundary);
    boundary.style.viewTimelineName = '--af-content';
    boundary.style.viewTimelineAxis = 'block';
    let parts;
    if (kind === 'headline') parts = [element];
    else {
      parts = [...element.children].filter(child => !child.matches('script'));
      if (!parts.length || /^(H[1-6]|P|A)$/.test(element.tagName)) {
        const copy = document.createElement('span'); copy.className = 'motion-copy';
        while (element.firstChild) copy.append(element.firstChild);
        element.append(copy); parts = [copy];
      }
    }
    parts.forEach((part, index) => {
      part.classList.add('motion-part', `motion-part--${kind}`);
      part.style.setProperty('--motion-start', `${Math.min(6, index * 2)}%`);
    });
    for (const number of boundary.querySelectorAll('[data-count]')) {
      number.setAttribute('aria-label', number.dataset.count);
    }
    fallbackParts.set(boundary, {parts, kind});
  }
  window.frontierMotion = {observe};
  for (const element of document.querySelectorAll('[data-motion]')) observe(element);
  for (const selector of ['.section-heading > *', '.stat-plate', '.stat-tile', '.showcase-field > *',
    '.timeline-tools', '.timeline-frame', '.collection-header > *', '.cta-inner > *', '.footer-brand', '.directory-heading > *']) {
    for (const element of document.querySelectorAll(selector)) observe(element);
  }
  const picture = document.querySelector('.masthead');
  if (picture) observe(picture, 'picture');
  let scheduled = false;
  function updateMotion() {
    if (scrollDriven || scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      if (!scrollDriven) for (const [boundary, {parts, kind}] of fallbackParts) {
        const bounds = boundary.getBoundingClientRect();
        const progress = Math.max(0, Math.min(1, (innerHeight - bounds.top) / (innerHeight + bounds.height)));
        const edge = progress < .2 ? 1 - progress / .2 : progress > .8 ? (progress - .8) / .2 : 0;
        for (const part of parts) {
          if (reducedMotion.matches) {part.style.removeProperty('opacity'); part.style.removeProperty('transform'); continue;}
          part.style.opacity = kind === 'picture' ? '1' : String(1 - edge * .6);
          const direction = progress < .2 ? 1 : -1;
          part.style.transform = kind === 'row' ? 'none' : kind === 'picture' ? `scale(${1 + edge * .025})` : `translateY(${direction * edge * 16}px)`;
        }
      }
      scheduled = false;
    });
  }
  addEventListener('scroll', updateMotion, {passive: true}); addEventListener('resize', updateMotion);
  reducedMotion.addEventListener('change', updateMotion);
  updateMotion();

  const pageLink = document.querySelector(`[data-page-link="${document.body.dataset.page}"]`);
  if (pageLink) pageLink.setAttribute('aria-current', 'page');
  if (document.body.dataset.page !== 'home') return;
  const links = [...document.querySelectorAll('.site-nav [data-section]')];
  let navigationFrame = 0;
  function updateNavigation() {
    if (navigationFrame) return;
    navigationFrame = requestAnimationFrame(() => {
      const line = document.querySelector('header').offsetHeight + innerHeight * .2;
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
