// Build the website from the same Markdown readers open on GitHub.
import { Marked, Renderer } from 'marked';
import { readFileSync } from 'node:fs';
import path from 'node:path';
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pages = JSON.parse(readFileSync(0, 'utf8'));
const results = pages.map(page => {
  const renderer = new Renderer();
  renderer.html = ({text}) => escape(text);
  renderer.link = function ({href, tokens}) {
    const text = this.parser.parseInline(tokens);
    if (!href) return text;
    href = href.trim();
    if (/^[a-z][a-z0-9+.-]*:/i.test(href) && !/^https?:\/\//i.test(href)) return text;
    let target;
    if (/^https?:\/\//i.test(href)) target = href;
    else {
      const [file, fragment] = href.split('#', 2);
      const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(page.markdown_path), file));
      if (resolved.startsWith('../') || resolved.startsWith('/')) return text;
      // PDF originals and crops are local-only; never create repository download links.
      if (/\.pdf(?:\?|$)/i.test(resolved)) return text;
      target = page.repository + '/blob/main/' + resolved.split('/').map(encodeURIComponent).join('/') + (fragment ? '#' + fragment : '');
    }
    return `<a href="${escape(target)}">${text}</a>`;
  };
  renderer.image = ({href, text}) => {
    const image = page.images[href];
    if (!image) throw new Error(`Unregistered Markdown image: ${href}`);
    return `<a class="inline-image" href="${escape(image.full)}" data-preview="{{asset_prefix}}${escape(image.preview)}" data-title="${escape(text)}"><img src="{{asset_prefix}}${escape(image.preview)}" width="${image.width}" height="${image.height}" alt="${escape(text)}" loading="lazy" decoding="async"></a>`;
  };
  return new Marked({renderer, gfm:true}).parse(page.markdown);
});
process.stdout.write(JSON.stringify(results));
