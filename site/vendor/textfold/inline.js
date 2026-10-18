// Mount TextFold in the existing page flow, with no iframe or inner scroll area.
(() => {
  const host = document.querySelector('[data-textfold-inline]');
  if (!host) return;
  const assets = new URL(host.dataset.assets, location.href);
  const dataUrl = new URL(host.dataset.document, location.href);
  const root = host.attachShadow({mode: 'open'});
  let ready = false;
  const hosted = selector => selector
    .replace(/(^|[\s,>+~(])(?:html|:root)((?:\[[^\]]*\]|\.[\w-]+|:not\([^)]*\))*)(?=[\s,>+~)]|$)/g,
      (_, before, qualifier) => `${before}:host${qualifier ? `(${qualifier})` : ''}`)
    .replace(/(^|[\s,>+~])body(?=[\s,.#:[>+~]|$)/g, '$1.reader-shell');
  function sheetFor(text) {
    const parsed = new CSSStyleSheet(); parsed.replaceSync(text);
    const walk = rules => [...rules].map(rule => {
      if (rule.selectorText !== undefined) return `${hosted(rule.selectorText)} {${rule.style.cssText}}`;
      if (rule.cssRules && !rule.name) {
        const header = rule.cssText.slice(0, rule.cssText.indexOf('{'));
        return `${header}{${walk(rule.cssRules)}}`;
      }
      return rule.cssText;
    }).join('\n');
    const sheet = new CSSStyleSheet(); sheet.replaceSync(walk(parsed.cssRules)); return sheet;
  }
  async function get(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Reader asset ${response.status}`);
    return response;
  }
  function script(name) {
    return new Promise((resolve, reject) => {
      const element = document.createElement('script');
      element.src = new URL(name, assets).href;
      element.onload = resolve; element.onerror = reject;
      document.head.append(element);
    });
  }
  function theme() { host.dataset.theme = document.documentElement.dataset.theme; }
  theme();
  new MutationObserver(theme).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
  const scrollToSection = id => {
    const section = root.getElementById(id);
    if (!section) return;
    section.scrollIntoView({block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
  };
  for (const link of document.querySelectorAll('[data-fold-section]')) {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
      event.preventDefault();
      const id = link.dataset.foldSection;
      if (ready) scrollToSection(id);
      else addEventListener('ai-frontier-reader-ready', () => scrollToSection(id), {once: true});
      history.replaceState(null, '', `#${encodeURIComponent(id)}`);
    });
  }
  addEventListener('ai-frontier-reader-ready', () => {
    ready = true; host.removeAttribute('aria-busy');
    host.querySelector('.textfold-loading')?.remove();
    if (location.hash) scrollToSection(decodeURIComponent(location.hash.slice(1)));
  }, {once: true});
  // Native figure enlargement locks this same document, then restores it.
  new MutationObserver(() => {
    const open = host.classList.contains('lb-open');
    document.documentElement.classList.toggle('textfold-lightbox-open', open);
  }).observe(host, {attributes: true, attributeFilter: ['class']});
  (async () => {
    try {
      const [shell, base, overrides, inline, data] = await Promise.all([
        get(new URL('inline.html', assets)).then(r => r.text()),
        get(new URL('reader.css', assets)).then(r => r.text()),
        get(new URL('site-overrides.css', assets)).then(r => r.text()),
        get(new URL('inline.css', assets)).then(r => r.text()),
        get(dataUrl).then(r => r.arrayBuffer()),
      ]);
      const stream = new Blob([data]).stream().pipeThrough(new DecompressionStream('gzip'));
      let json = await new Response(stream).text();
      json = json.replaceAll('../../assets/textfold-images/', new URL('../textfold-images/', assets).href);
      const documentData = JSON.parse(json);
      documentData.katex = new URL('katex/', assets).href;
      root.innerHTML = shell;
      root.adoptedStyleSheets = [sheetFor(base), sheetFor(overrides), sheetFor(inline)];
      root.getElementById('paper-data').textContent = JSON.stringify(documentData);
      await script('i18n.js');
      await script('reader.js');
      if (!ready) throw new Error('Reader did not initialize');
      // Update the site's existing progress indicator after the full text arrives.
      dispatchEvent(new Event('scroll'));
    } catch (error) {
      root.replaceChildren(); host.removeAttribute('aria-busy');
      const loading = host.querySelector('.textfold-loading');
      if (loading) { loading.textContent = host.dataset.ui === 'zh' ? '全文加载失败，请打开官方来源。' : 'Full text could not load. Open the official source.'; loading.setAttribute('role', 'alert'); }
    }
  })();
})();
