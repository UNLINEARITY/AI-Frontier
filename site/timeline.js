/* One date axis for every model. Vertical offsets only keep nearby points legible. */
(() => {
  const section = document.querySelector('#timeline');
  if (!section) return;
  const data = JSON.parse(document.querySelector('#timeline-data').textContent);
  const day = 86400000;
  const chinese = document.documentElement.lang.startsWith('zh');
  const svg = document.querySelector('#timeline-plot');
  const frame = document.querySelector('.timeline-frame');
  const plot = document.querySelector('#timeline-points');
  const ticks = document.querySelector('#timeline-ticks');
  const input = document.querySelector('#timeline-search');
  const tooltip = document.querySelector('#timeline-tooltip');
  const directoryLink = document.querySelector('#timeline-models-link');
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase().replaceAll('π', 'pi').replace(/[^\p{L}\p{N}]/gu, '');
  for (const model of data) model.searchTerms = normalize(`${model.model} ${model.vendor} ${model.publisher_en} ${model.publisher_cn} ${(model.aliases || []).join(' ')}`);
  const dated = data.filter(model => model.release_date).map(model => ({...model, time: Date.parse(model.release_date + 'T00:00:00Z')}));
  const undated = data.filter(model => !model.release_date);
  const full = dated.length ? [Math.min(...dated.map(m => m.time)), Math.max(...dated.map(m => m.time))] : [Date.now() - day, Date.now()];
  if (full[1] - full[0] < 3 * day) {full[0] -= day * 2; full[1] += day * 2;}
  const minimumSpan = Math.min(3 * day, full[1] - full[0]);
  let view = [...full], target = [...full], width = 0, height = 304, animation = 0;
  let publisher = '';
  let activeNode = null;
  const pointers = new Map();
  let gesture = null, suppressClickUntil = 0, urlTimer = 0;
  const params = new URLSearchParams(location.search);
  publisher = params.get('publisher') || '';
  input.value = params.get('model') || '';
  let searchTerms = queryTerms();
  const from = Date.parse(params.get('from') || ''), to = Date.parse(params.get('to') || '');
  if (Number.isFinite(from) && Number.isFinite(to) && from < to) view = target = constrain(from, to);

  function element(tag, attributes = {}, text = '') {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    node.textContent = text;
    return node;
  }
  function label(model) {return chinese ? model.publisher_cn : model.publisher_en;}
  function queryTerms() {return input.value.trim().split(/\s+/).map(normalize).filter(Boolean);}
  function matches(model) {
    return (!publisher || model.vendor === publisher) && searchTerms.every(term => model.searchTerms.includes(term));
  }
  function dateText(time) {return new Date(time).toISOString().slice(0, 10);}
  function constrain(start, end) {
    const span = Math.max(minimumSpan, Math.min(full[1] - full[0], end - start));
    start = Math.max(full[0], Math.min(full[1] - span, (start + end - span) / 2));
    return [start, start + span];
  }
  function x(time) {return 16 + (time - view[0]) / (view[1] - view[0]) * Math.max(1, width - 32);}
  function timeAt(pixel, range = target) {return range[0] + (pixel - 16) / Math.max(1, width - 32) * (range[1] - range[0]);}
  function windowQuery() {
    const state = new URLSearchParams(location.search);
    state.delete('model'); state.delete('from'); state.delete('to');
    if (input.value.trim()) state.set('model', input.value.trim());
    if (target[1] - target[0] < (full[1] - full[0]) * .999) {
      state.set('from', new Date(target[0]).toISOString()); state.set('to', new Date(target[1]).toISOString());
    }
    return state;
  }
  function persistURL() {
    clearTimeout(urlTimer);
    urlTimer = 0;
    const state = windowQuery();
    const suffix = state.size ? `?${state}` : '';
    const destination = `${location.pathname}${suffix}#timeline`;
    if (destination !== `${location.pathname}${location.search}${location.hash}`) history.replaceState(null, '', destination);
    syncLanguage(state);
  }
  function syncLanguage(state) {
    const language = document.querySelector('.language-link');
    const destination = new URL(language.href);
    destination.search = state.toString(); destination.hash = 'timeline'; language.href = destination.href;
  }
  function updateURL() {
    syncLanguage(windowQuery());
    // Continuous gestures update the plot immediately, but coalesce browser history writes.
    clearTimeout(urlTimer);
    urlTimer = setTimeout(persistURL, 150);
  }
  function setWindow(start, end, animate = false) {
    cancelAnimationFrame(animation);
    target = constrain(start, end);
    updateURL();
    if (!animate || reducedMotion.matches) {section.setAttribute('aria-busy', 'false'); view = [...target]; render(); return;}
    section.setAttribute('aria-busy', 'true');
    const initial = [...view], began = performance.now();
    function tick(now) {
      const fraction = Math.min(1, (now - began) / 260);
      const eased = 1 - Math.pow(1 - fraction, 3);
      view = initial.map((value, index) => value + (target[index] - value) * eased);
      render();
      if (fraction < 1) animation = requestAnimationFrame(tick);
      else section.setAttribute('aria-busy', 'false');
    }
    animation = requestAnimationFrame(tick);
  }
  function zoom(factor, anchor = width / 2) {
    const position = Math.max(0, Math.min(1, (anchor - 16) / Math.max(1, width - 32)));
    const time = target[0] + position * (target[1] - target[0]);
    const span = (target[1] - target[0]) / factor;
    setWindow(time - position * span, time + (1 - position) * span, true);
  }
  function showTooltip(item) {
    activeNode = item;
    document.querySelector('#timeline-tooltip-publisher').textContent = label(item.model);
    document.querySelector('#timeline-tooltip-model').textContent = item.model.model;
    const time = document.querySelector('#timeline-tooltip-date');
    time.textContent = item.model.release_date; time.dateTime = item.model.release_date;
    const logo = document.querySelector('#timeline-tooltip-logo');
    logo.hidden = !item.model.logo;
    if (item.model.logo) logo.src = section.dataset.prefix + item.model.logo;
    tooltip.hidden = false;
    item.link.setAttribute('aria-describedby', 'timeline-tooltip');
    positionTooltip();
  }
  function hideTooltip() {
    activeNode?.link.removeAttribute('aria-describedby');
    activeNode = null; tooltip.hidden = true;
  }
  function positionTooltip() {
    if (!activeNode) return;
    tooltip.style.left = `${Math.max(8, Math.min(width - tooltip.offsetWidth - 8, activeNode.x + 14))}px`;
    const top = activeNode.y > height / 2 ? activeNode.y - tooltip.offsetHeight - 16 : activeNode.y + 16;
    tooltip.style.top = `${Math.max(8, Math.min(height - tooltip.offsetHeight - 8, top))}px`;
  }
  const nodes = dated.map(model => {
    const link = element('a', {href: model.href, class: 'timeline-node', tabindex: '0', 'data-date': model.release_date,
      'data-model': model.model, 'aria-label': `${model.model} · ${label(model)} · ${model.release_date}`});
    const stem = element('line', {class: 'timeline-stem'});
    const hit = element('circle', {class: 'timeline-hit', r: 13});
    const dot = element('circle', {class: 'timeline-dot', r: 5});
    const name = element('text', {class: 'timeline-model-label', x: 12, y: 3});
    link.append(stem, hit, dot, name); plot.append(link);
    const item = {model, link, stem, name, x: 0, y: 0};
    link.addEventListener('pointerenter', () => {if (!gesture) showTooltip(item);});
    link.addEventListener('pointerleave', () => {if (document.activeElement !== link) hideTooltip();});
    link.addEventListener('focus', () => {
      if (model.time < target[0] || model.time > target[1]) {
        const span = target[1] - target[0]; setWindow(model.time - span / 2, model.time + span / 2);
      }
      showTooltip(item);
    });
    link.addEventListener('blur', hideTooltip);
    return item;
  });
  function tickDates() {
    const span = view[1] - view[0];
    const maximum = Math.max(2, Math.floor(width / 95));
    const dates = [];
    if (span / maximum > 25 * day) {
      const desired = span / maximum / (30 * day);
      const months = [1, 3, 6, 12, 24, 60].find(step => step >= desired) || 120;
      const start = new Date(view[0]);
      let month = start.getUTCFullYear() * 12 + start.getUTCMonth();
      month = Math.ceil(month / months) * months;
      for (; ; month += months) {
        const time = Date.UTC(Math.floor(month / 12), month % 12, 1);
        if (time > view[1]) break;
        if (time >= view[0]) dates.push([time, new Intl.DateTimeFormat(chinese ? 'zh-CN' : 'en', {timeZone: 'UTC', year: 'numeric', ...(months < 12 ? {month: 'short'} : {})}).format(time)]);
      }
    } else {
      const step = [1, 2, 7, 14, 28].find(days => days * day >= span / maximum) || 28;
      for (let time = Math.ceil(view[0] / (step * day)) * step * day; time <= view[1]; time += step * day) {
        dates.push([time, new Intl.DateTimeFormat(chinese ? 'zh-CN' : 'en', {timeZone: 'UTC', month: 'short', day: 'numeric'}).format(time)]);
      }
    }
    return dates;
  }
  function render() {
    const focusedNode = nodes.find(item => item.link === document.activeElement);
    const axis = Math.round(height / 2);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.dataset.from = dateText(view[0]); svg.dataset.to = dateText(view[1]);
    document.querySelector('#timeline-clip-rect').setAttribute('width', width);
    document.querySelector('#timeline-clip-rect').setAttribute('height', height);
    document.querySelector('#timeline-axis').setAttribute('d', `M16 ${axis}H${width - 16}`);
    ticks.replaceChildren();
    for (const [time, text] of tickDates()) {
      const group = element('g', {class: 'timeline-tick', transform: `translate(${x(time)},0)`});
      group.append(element('line', {x1: 0, x2: 0, y1: 24, y2: height - 38}),
                   element('text', {x: 0, y: height - 16, 'text-anchor': 'middle'}, text));
      ticks.append(group);
    }
    const offsets = [0, -22, 22, -44, 44, -66, 66, -88, 88];
    const occupied = offsets.map(() => -Infinity);
    let visible = 0, matching = 0;
    for (const item of nodes) {
      const pass = matches(item.model);
      if (pass) matching++;
      const position = x(item.model.time);
      const onScreen = pass && position >= 8 && position <= width - 8;
      item.link.style.display = onScreen ? '' : 'none';
      if (!onScreen) continue;
      let lane = occupied.findIndex(previous => position - previous >= 16);
      if (lane < 0) lane = occupied.indexOf(Math.min(...occupied));
      occupied[lane] = position;
      item.x = position; item.y = axis + offsets[lane];
      item.link.setAttribute('transform', `translate(${position},${item.y})`);
      item.stem.setAttribute('x1', 0); item.stem.setAttribute('x2', 0);
      item.stem.setAttribute('y1', 0); item.stem.setAttribute('y2', -offsets[lane]);
      item.name.style.display = 'none';
      visible++;
    }
    // Labels yield to nearby labels; every point retains its full accessible name and tooltip.
    const boxes = [];
    for (const item of [...nodes].reverse()) if (item.link.style.display !== 'none') {
      const text = [...item.model.model];
      item.name.textContent = text.length > 24 ? text.slice(0, 21).join('') + '…' : item.model.model;
      const size = item.name.textContent.length * 6;
      const directions = item.x + size + 14 > width - 12 ? [true, false] : [false, true];
      for (const leftward of directions) {
        const left = leftward ? item.x - size - 12 : item.x + 12;
        const box = [left, item.y - 7, left + size, item.y + 7];
        const collidesWithPoint = nodes.some(other => other !== item && other.link.style.display !== 'none' &&
          other.x + 8 > box[0] && other.x - 8 < box[2] && other.y + 8 > box[1] && other.y - 8 < box[3]);
        if (left < 6 || left + size > width - 6 || collidesWithPoint ||
            boxes.some(b => box[0] < b[2] + 5 && box[2] + 5 > b[0] && box[1] < b[3] + 4 && box[3] + 4 > b[1])) continue;
        item.name.setAttribute('x', leftward ? -12 : 12); item.name.setAttribute('text-anchor', leftward ? 'end' : 'start');
        item.name.style.display = ''; boxes.push(box); break;
      }
    }
    let unconfirmed = 0;
    for (const model of undated) if (matches(model)) unconfirmed++;
    const unconfirmedLabel = document.querySelector('#timeline-undated-count');
    unconfirmedLabel.hidden = unconfirmed === 0;
    unconfirmedLabel.textContent = `${unconfirmed} ${unconfirmedLabel.dataset.label}`;
    const directoryQuery = new URLSearchParams();
    if (publisher) directoryQuery.set('publisher', publisher);
    if (input.value.trim()) directoryQuery.set('q', input.value.trim());
    directoryLink.href = 'models.html' + (directoryQuery.size ? `?${directoryQuery}` : '');
    const empty = document.querySelector('#timeline-empty');
    empty.toggleAttribute('hidden', visible !== 0); empty.setAttribute('x', width / 2); empty.setAttribute('y', axis - 24);
    const count = section.dataset.countLabel;
    document.querySelector('#timeline-visible-count').textContent = `${visible} / ${matching} ${count}`;
    document.querySelector('#timeline-range').textContent = dated.length ? `${dateText(view[0])} — ${dateText(view[1])}` : '';
    const scale = (full[1] - full[0]) / (view[1] - view[0]);
    document.querySelector('#timeline-zoom').textContent = `${scale < 10 ? scale.toFixed(1).replace(/\.0$/, '') : Math.round(scale)}×`;
    document.querySelector('#timeline-out').disabled = scale <= 1.001;
    document.querySelector('#timeline-in').disabled = view[1] - view[0] <= minimumSpan * 1.001;
    if (activeNode && activeNode.link.style.display === 'none') hideTooltip();
    else positionTooltip();
    if (focusedNode?.link.style.display === 'none') svg.focus({preventScroll: true});
  }
  document.querySelector('#timeline-in').addEventListener('click', () => zoom(2));
  document.querySelector('#timeline-out').addEventListener('click', () => zoom(.5));
  document.querySelector('#timeline-fit').addEventListener('click', () => setWindow(...full, true));
  document.querySelector('#timeline-latest').addEventListener('click', () => setWindow(full[1] - 120 * day, full[1], true));
  input.addEventListener('input', () => {
    searchTerms = queryTerms();
    hideTooltip();
    const found = dated.filter(matches);
    if (input.value.trim() && found.length) {
      const earliest = Math.min(...found.map(m => m.time)), latest = Math.max(...found.map(m => m.time));
      const padding = Math.max(3 * day, (latest - earliest) * .05);
      setWindow(earliest - padding, latest + padding, true);
    } else {updateURL(); render();}
  });
  document.addEventListener('frontier:publisher', event => {publisher = event.detail; hideTooltip(); render();});
  document.addEventListener('frontier:reset', () => {
    input.value = ''; searchTerms = queryTerms(); hideTooltip(); setWindow(...full, true);
  });
  svg.addEventListener('wheel', event => {
    if (event.ctrlKey || event.metaKey) {
      event.preventDefault(); zoom(Math.exp(-Math.max(-100, Math.min(100, event.deltaY)) * .012), event.clientX - svg.getBoundingClientRect().left);
    } else if (event.shiftKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) {
      event.preventDefault();
      const shift = (event.deltaX || event.deltaY) / Math.max(1, width - 32) * (target[1] - target[0]);
      setWindow(target[0] + shift, target[1] + shift);
    }
  }, {passive: false});
  svg.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    const positions = [...pointers.values()];
    gesture = {start: [...target], x: event.clientX, y: event.clientY, moved: false,
      distance: positions.length === 2 ? Math.hypot(positions[1].x - positions[0].x, positions[1].y - positions[0].y) : 0,
      center: positions.length === 2 ? (positions[0].x + positions[1].x) / 2 - svg.getBoundingClientRect().left : 0};
  });
  svg.addEventListener('pointermove', event => {
    if (!gesture || !pointers.has(event.pointerId)) return;
    pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    const positions = [...pointers.values()];
    if (positions.length === 2 && gesture.distance > 0) {
      const distance = Math.max(1, Math.hypot(positions[1].x - positions[0].x, positions[1].y - positions[0].y));
      const center = (positions[0].x + positions[1].x) / 2 - svg.getBoundingClientRect().left;
      const ratio = (center - 16) / Math.max(1, width - 32);
      const anchor = timeAt(gesture.center, gesture.start);
      const span = (gesture.start[1] - gesture.start[0]) * gesture.distance / distance;
      setWindow(anchor - ratio * span, anchor + (1 - ratio) * span);
      gesture.moved = true;
    } else {
      const movement = event.clientX - gesture.x;
      if (!gesture.moved && Math.abs(movement) < 5) return;
      if (!gesture.moved && event.pointerType === 'touch' && Math.abs(movement) < Math.abs(event.clientY - gesture.y)) return;
      gesture.moved = true;
      const shift = -movement / Math.max(1, width - 32) * (gesture.start[1] - gesture.start[0]);
      setWindow(gesture.start[0] + shift, gesture.start[1] + shift);
    }
    hideTooltip(); svg.classList.add('is-dragging'); svg.setPointerCapture(event.pointerId);
  });
  function endGesture(event) {
    if (gesture?.moved) suppressClickUntil = performance.now() + 200;
    pointers.delete(event.pointerId); gesture = null; svg.classList.remove('is-dragging');
    if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId);
    if (urlTimer) persistURL();
  }
  svg.addEventListener('pointerup', endGesture); svg.addEventListener('pointercancel', endGesture);
  addEventListener('pointerup', event => {if (pointers.has(event.pointerId)) endGesture(event);});
  // Save the latest view before following a reader/language link or leaving the page.
  document.addEventListener('click', event => {if (urlTimer && event.target.closest('a[href]')) persistURL();}, true);
  addEventListener('pagehide', () => {if (urlTimer) persistURL();});
  svg.addEventListener('click', event => {if (event.detail > 0 && performance.now() < suppressClickUntil) event.preventDefault();}, true);
  svg.addEventListener('keydown', event => {
    if (event.key === 'Escape') {hideTooltip(); return;}
    if (event.key === '+' || event.key === '=') {event.preventDefault(); zoom(2);}
    else if (event.key === '-') {event.preventDefault(); zoom(.5);}
    else if (event.key === 'Home') {event.preventDefault(); setWindow(...full, true);}
    else if (['ArrowLeft', 'ArrowRight'].includes(event.key)) {
      event.preventDefault();
      const selected = nodes.findIndex(item => item.link === document.activeElement);
      const direction = event.key === 'ArrowRight' ? 1 : -1;
      if (selected >= 0) {
        const next = nodes.slice(selected + 1).find(item => matches(item.model));
        const previous = nodes.slice(0, selected).reverse().find(item => matches(item.model));
        const item = direction > 0 ? next : previous;
        if (item) {
          const span = target[1] - target[0];
          if (item.model.time < target[0] || item.model.time > target[1]) setWindow(item.model.time - span / 2, item.model.time + span / 2);
          item.link.focus();
        }
      } else {
        const shift = direction * (target[1] - target[0]) * .2;
        setWindow(target[0] + shift, target[1] + shift, true);
      }
    }
  });
  new ResizeObserver(() => {width = frame.clientWidth; height = svg.clientHeight; render();}).observe(frame);
})();
