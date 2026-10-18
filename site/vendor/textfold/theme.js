// The embedding AI Frontier page owns the color choice.
(() => {
  let pendingSection = null;
  const setTheme = (theme) => {
    if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme;
  };
  const goToSection = (id) => {
    if (typeof id !== 'string' || !id) return;
    const section = document.getElementById(id);
    if (!section?.classList.contains('chunk')) { pendingSection = id; return; }
    pendingSection = null;
    section.scrollIntoView({
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start',
    });
  };
  addEventListener('message', (event) => {
    if (event.origin !== location.origin || event.source !== parent) return;
    if (event.data?.type === 'ai-frontier-theme') setTheme(event.data.theme);
    if (event.data?.type === 'ai-frontier-section') goToSection(event.data.id);
  });
  addEventListener('ai-frontier-reader-ready', () => {
    if (pendingSection) goToSection(pendingSection);
  });
  try {
    const hash = decodeURIComponent(location.hash.slice(1).split('&', 1)[0]);
    if (hash && !/^(lang|level)=/.test(hash)) pendingSection = hash;
  } catch { /* malformed fragment */ }
  if (parent !== window) document.documentElement.classList.add('embedded');
  let chosen;
  try { chosen = localStorage.getItem('ai-frontier-theme'); } catch { /* Optional storage. */ }
  setTheme(chosen === 'light' || chosen === 'dark' ? chosen :
    (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
})();
