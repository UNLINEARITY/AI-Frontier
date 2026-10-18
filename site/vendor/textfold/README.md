# TextFold static reader assets

The native reader files in this directory are adapted from TextFold at commit
`2cd77e0987b590f9f67154bcdda76c59e6870b73` (Apache-2.0). The vendored reader
keeps TextFold's own document rendering, five-level zoom, citations, notes and
keyboard controls. The site adapter uses system fonts, the AI Frontier theme,
local images, and the original document language. It disables controls that
depend on a model service.

The project uses TextFold's first-sentence local ladders. The labels identify
word and sentence excerpts and do not describe them as generated summaries.
No model calls or translations are used in published reader pages.
Each reader page loads its matching gzip-compressed `.tfd` payload and expands
it with the browser's `DecompressionStream` API. `inline.js` mounts the native
document in the existing page flow, using its font, width, paper and scroll.
Only the five-level control stays fixed at the bottom of the viewport. A shadow
root isolates document styles; it creates no frame or independent scroll area.
Original site navigation remains outside that root. Source images and KaTeX
URLs resolve against the shared site assets for both language routes.
Inline zoom uses the native continuous position, drag and snap motion in the
document itself. Its paragraph anchor stays in the page scroll; browser scroll
anchoring is disabled on these pages. The selected level is kept across article
and language navigation in local storage. Responsive image sizing covers both
figure bodies and raw OCR paragraphs.

`reader.js`, `reader.css`, `template.html`, `site-overrides.css`, `theme.js` and `inline.*`
contain local modifications. TextFold's Apache license and attribution are in
`LICENSE` and `NOTICE`. KaTeX is separately licensed under MIT; its license is
in `katex/LICENSE`. KaTeX's mathematical fonts are included; the reader's
general text uses system fonts. Upstream PDF.js assets and application/server
code are not included.
