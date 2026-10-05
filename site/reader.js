const viewer = document.querySelector('.image-viewer');
const viewerImage = document.querySelector('#viewer-image');
let opener;
for (const button of document.querySelectorAll('[data-preview]')) button.addEventListener('click', () => {
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
