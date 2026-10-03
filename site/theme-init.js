// Apply the preference before the stylesheet paints, including on language changes.
(() => {
  let preference = 'system';
  try {
    const saved = localStorage.getItem('ai-frontier-theme');
    if (['system', 'light', 'dark'].includes(saved)) preference = saved;
  } catch { /* Storage can be unavailable in private or restricted contexts. */ }
  const dark = preference === 'dark' || (preference === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  document.documentElement.dataset.themePreference = preference;
})();
