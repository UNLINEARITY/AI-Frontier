const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const systemTheme = matchMedia('(prefers-color-scheme: dark)');
const themeMenu = document.querySelector('.theme-menu');
let themePreference = document.documentElement.dataset.themePreference || 'system';
let themeTransition;
function updateThemeControls() {
  for (const button of document.querySelectorAll('[data-theme-choice]')) button.setAttribute('aria-pressed', String(button.dataset.themeChoice === themePreference));
  document.querySelector('meta[name="theme-color"]').content = document.documentElement.dataset.theme === 'dark' ? '#09121e' : '#f6f8fb';
}
function applyTheme(preference, animate = true) {
  themePreference = preference;
  try {localStorage.setItem('ai-frontier-theme', preference);} catch { /* Optional persistence. */ }
  const theme = preference === 'system' ? (systemTheme.matches ? 'dark' : 'light') : preference;
  const update = () => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.themePreference = preference;
    updateThemeControls();
  };
  if (animate && !reducedMotion.matches && document.startViewTransition && document.documentElement.dataset.theme !== theme) {
    themeTransition?.skipTransition();
    themeTransition = document.startViewTransition(update);
    themeTransition.finished.catch(() => {});
  }
  else update();
}
for (const button of document.querySelectorAll('[data-theme-choice]')) button.addEventListener('click', () => {
  themeMenu.open = false;
  applyTheme(button.dataset.themeChoice);
  themeMenu.querySelector('summary').focus({preventScroll: true});
});
addEventListener('storage', event => {
  if (event.key === 'ai-frontier-theme') applyTheme(['system', 'light', 'dark'].includes(event.newValue) ? event.newValue : 'system', false);
});
systemTheme.addEventListener('change', () => {if (themePreference === 'system') applyTheme('system', false);});
document.addEventListener('click', event => {if (!themeMenu.contains(event.target)) themeMenu.open = false;});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && themeMenu.open) {themeMenu.open = false; themeMenu.querySelector('summary').focus();}
});
updateThemeControls();
let scheduled = false;
function scrollFeedback() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => {
    const height = document.documentElement.scrollHeight - innerHeight;
    document.querySelector('.reading-progress').style.transform = `scaleX(${height > 0 ? scrollY / height : 0})`;
    document.querySelector('#back-top').hidden = scrollY < 700;
    document.querySelector('header').classList.toggle('scrolled', scrollY > 20);
    scheduled = false;
  });
}
addEventListener('scroll', scrollFeedback, {passive: true});
document.querySelector('#back-top').addEventListener('click', () => scrollTo({top: 0, behavior: reducedMotion.matches ? 'instant' : 'smooth'}));

scrollFeedback();
