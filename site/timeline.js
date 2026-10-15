/* A proportional detail timeline with progressive labels and a global brush. */
(() => {
  const section = document.querySelector('#timeline');
  if (!section) return;
  const data = JSON.parse(document.querySelector('#timeline-data').textContent);
  const day = 86400000, padding = 28;
  const chinese = document.documentElement.lang.startsWith('zh');
  const svg = document.querySelector('#timeline-plot'), frame = document.querySelector('.timeline-frame');
  const stems = document.querySelector('#timeline-stems');
  const plot = document.querySelector('#timeline-points'), ticks = document.querySelector('#timeline-ticks');
  const explorer = window.frontierModels;
  const tooltip = document.querySelector('#timeline-tooltip'), guide = document.querySelector('#timeline-guide');
  const layout = window.frontierTimelineLayout;
  const measureContext = document.createElement('canvas').getContext('2d');
  measureContext.font = `500 14px ${getComputedStyle(svg).fontFamily}`;
  const measure = text => measureContext.measureText(text).width;
  for (const model of data) model.searchTerms = explorer.searchText(model);
  const dated = data.filter(model => model.release_date).map(model => ({...model, time: Date.parse(model.release_date + 'T00:00:00Z')}));
  const undated = data.filter(model => !model.release_date);
  const full = dated.length ? [Math.min(...dated.map(m => m.time)), Math.max(...dated.map(m => m.time))] : [Date.now() - day, Date.now()];
  if (full[1] - full[0] < 3 * day) {full[0] -= day * 2; full[1] += day * 2;}
  const fullSpan = full[1] - full[0], minimumSpan = Math.min(3 * day, fullSpan);
  let view = [...full], target = [...full], width = frame.clientWidth, height = svg.clientHeight, axis = 180, animation = 0;
  let phase = 'idle', focusTimer = 0, focusGeneration = 0, lastWindow = '', leavingForChooser = false;
  let activeNode = null, visibleItems = [], filterVersion = 0, scopeKey = '', motionTimer = 0;
  const pointers = new Map();
  let gesture = null, suppressClickUntil = 0, urlTimer = 0;
  const params = new URLSearchParams(location.search);
  if (window.frontierEntry?.kind === 'models-enter' && explorer.publisher() && !reducedMotion.matches) phase = 'overview';
  section.dataset.phase = phase;

  function element(tag, attributes = {}, text = '') {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    node.textContent = text;
    return node;
  }
  function label(model) {return chinese ? model.publisher_cn : model.publisher_en;}
  function matches(model) {return explorer.matches(model);}
  function dateText(time) {return new Date(time).toISOString().slice(0, 10);}
  function maximumSpan() {return fullSpan;}
  function constrain(start, end) {
    start = Math.round(start); end = Math.round(end);
    const span = Math.floor(Math.max(minimumSpan, Math.min(maximumSpan(), end - start)));
    start = Math.round(Math.max(full[0], Math.min(full[1] - span, (start + end - span) / 2)));
    return [start, start + span];
  }
  function x(time) {return padding + (time - view[0]) / (view[1] - view[0]) * (width - 2 * padding);}
  function timeAt(pixel, range = target) {return range[0] + (pixel - padding) / Math.max(1, width - 2 * padding) * (range[1] - range[0]);}
  function persistURL() {clearTimeout(urlTimer); urlTimer = 0; explorer.persistWindow(target[0], target[1], isFull(target));}
  function updateURL() {clearTimeout(urlTimer); urlTimer = setTimeout(persistURL, 150);}
  function settle() {clearTimeout(motionTimer); delete section.dataset.moving; render();}
  function setWindow(start, end, animate = false, duration = 300) {
    cancelAnimationFrame(animation);
    target = constrain(start, end); updateURL(); hideGuide();
    clearTimeout(motionTimer);
    if (!reducedMotion.matches) section.dataset.moving = 'true';
    if (!animate || reducedMotion.matches) {
      section.setAttribute('aria-busy', 'false'); view = [...target];
      if (reducedMotion.matches) delete section.dataset.moving;
      render();
      if (!reducedMotion.matches) motionTimer = setTimeout(settle, 110);
      return;
    }
    section.setAttribute('aria-busy', 'true');
    const initial = constrain(...view), began = performance.now();
    function tick(now) {
      const fraction = Math.min(1, (now - began) / duration), eased = 1 - Math.pow(1 - fraction, 3);
      view = initial.map((value, index) => value + (target[index] - value) * eased);
      if (fraction < 1) {render(); animation = requestAnimationFrame(tick);}
      else {section.setAttribute('aria-busy', 'false'); settle();}
    }
    animation = requestAnimationFrame(tick);
  }
  function zoom(factor, anchor = width / 2, animate = true) {
    const position = Math.max(0, Math.min(1, (anchor - padding) / Math.max(1, width - 2 * padding)));
    const time = target[0] + position * (target[1] - target[0]), span = (target[1] - target[0]) / factor;
    setWindow(time - position * span, time + (1 - position) * span, animate);
  }
  function showGuide(time) {
    time = Math.max(full[0], Math.min(full[1], Math.round(time / day) * day));
    const position = x(time);
    const left = Math.max(8, Math.min(width - 110, position - 51));
    guide.removeAttribute('hidden');
    const line = guide.querySelector('line');
    for (const [key, value] of Object.entries({x1: position, x2: position, y1: 38, y2: height - 44})) line.setAttribute(key, value);
    const box = guide.querySelector('rect'); box.setAttribute('x', left); box.setAttribute('y', height - 39);
    const text = guide.querySelector('text'); text.setAttribute('x', left + 51); text.setAttribute('y', height - 20); text.textContent = dateText(time);
  }
  function hideGuide() {guide.setAttribute('hidden', '');}
  function showTooltip(item) {
    activeNode?.link.removeAttribute('aria-describedby'); activeNode?.stem.classList.remove('is-active'); activeNode = item;
    item.stem.classList.add('is-active'); section.dataset.active = 'true';
    document.querySelector('#timeline-tooltip-publisher').textContent = label(item.model);
    document.querySelector('#timeline-tooltip-model').textContent = item.model.model;
    const time = document.querySelector('#timeline-tooltip-date');
    time.textContent = item.model.release_date; time.dateTime = item.model.release_date;
    const logo = document.querySelector('#timeline-tooltip-logo'); logo.hidden = !item.model.logo;
    if (item.model.logo) logo.src = section.dataset.prefix + item.model.logo;
    tooltip.hidden = false; item.link.setAttribute('aria-describedby', 'timeline-tooltip');
    showGuide(item.model.time); positionTooltip();
  }
  function hideTooltip() {activeNode?.link.removeAttribute('aria-describedby'); activeNode?.stem.classList.remove('is-active'); activeNode = null; delete section.dataset.active; tooltip.hidden = true; hideGuide();}
  function positionTooltip() {
    if (!activeNode) return;
    tooltip.style.left = `${Math.max(8, Math.min(width - tooltip.offsetWidth - 8, activeNode.x + 14))}px`;
    const top = activeNode.y > height / 2 ? activeNode.y - tooltip.offsetHeight - 24 : activeNode.y + 24;
    tooltip.style.top = `${Math.max(8, Math.min(height - tooltip.offsetHeight - 44, top))}px`;
  }
  const nodes = dated.map(model => {
    const lines = layout.wrapName(model.model, measure);
    const link = element('a', {href: model.href, class: 'timeline-node', tabindex: '0', 'data-date': model.release_date,
      'data-model': model.model, 'data-vendor': model.vendor, 'aria-label': `${model.model} · ${label(model)} · ${model.release_date}`});
    if (/^https?:/.test(model.href)) {link.setAttribute('target', '_blank'); link.setAttribute('rel', 'noopener');}
    const stem = element('line', {class: 'timeline-stem'}), hit = element('rect', {class: 'timeline-hit'});
    const dot = element('circle', {class: 'timeline-dot', r: 4.5}), name = element('text', {class: 'timeline-model-label'});
    for (const line of lines) name.append(element('tspan', {}, line));
    stems.append(stem); link.append(hit, dot, name); plot.append(link);
    const item = {model, link, stem, hit, name, x: 0, y: 0, time: model.time, lines, textWidth: Math.max(...lines.map(measure))};
    link.timelineItem = item;
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
  function refreshScope() {
    const context = phase === 'overview' || phase === 'highlight';
    const key = `${context}:${filterVersion}:${width.toFixed(2)}`;
    if (scopeKey === key) return;
    scopeKey = key;
    visibleItems = nodes.filter(item => context || matches(item.model));

    for (const item of nodes) {
      const pass = matches(item.model);
      item.link.dataset.selected = item.stem.dataset.selected = String(pass);
      item.link.style.display = item.stem.style.display = context || pass ? '' : 'none';
      item.link.setAttribute('tabindex', pass ? '0' : '-1'); item.link.style.pointerEvents = pass ? '' : 'none';
    }
  }
  function drawLayout() {
    const arrangement = layout.scatter(visibleItems, view, width, height);
    axis = arrangement.axis;
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    const clip = document.querySelector('#timeline-clip-rect'); clip.setAttribute('width', width); clip.setAttribute('height', height);
    document.querySelector('#timeline-axis').setAttribute('d', `M${padding} ${axis}H${width - padding}`);
    const onScreen = new Set(arrangement.items.map(item => item.link));
    for (const item of nodes) item.link.style.display = item.stem.style.display = onScreen.has(item.link) ? '' : 'none';
    const names = section.dataset.moving ? new Map() : layout.labelPositions(arrangement.items, width, height);
    for (const position of arrangement.items) {
      const item = position.link.timelineItem;
      item.x = position.x; item.y = position.y;
      item.link.setAttribute('transform', `translate(${item.x},${item.y})`);
      item.stem.setAttribute('transform', `translate(${item.x},${item.y})`);
      item.stem.setAttribute('x1', 0); item.stem.setAttribute('x2', 0); item.stem.setAttribute('y1', 0); item.stem.setAttribute('y2', axis - item.y);
      item.link.querySelector('.timeline-dot').setAttribute('r', position.radius);
      item.link.dataset.smallDot = String(position.radius < 2.4);
      const box = names.get(item.link);
      item.name.style.display = box ? '' : 'none'; item.link.dataset.labelVisible = String(Boolean(box));
      if (box) for (const [index, span] of [...item.name.children].entries()) {span.setAttribute('x', box.left - item.x); span.setAttribute('y', box.top - item.y + 14 + index * 18);}
      for (const [key, value] of Object.entries({x: -8, y: -8, width: 16, height: 16})) item.hit.setAttribute(key, value);
    }
  }
  const formats = {
    year: new Intl.DateTimeFormat(chinese ? 'zh-CN' : 'en', {timeZone: 'UTC', year: 'numeric'}),
    month: new Intl.DateTimeFormat(chinese ? 'zh-CN' : 'en', {timeZone: 'UTC', month: 'short'}),
    day: new Intl.DateTimeFormat(chinese ? 'zh-CN' : 'en', {timeZone: 'UTC', month: 'short', day: 'numeric'})
  };
  function drawCalendar() {
    ticks.replaceChildren();
    const calendar = layout.calendarTicks(view, width - 2 * padding);
    for (const time of calendar.dates) {
      const group = element('g', {class: 'timeline-tick', transform: `translate(${x(time)},0)`});
      const text = formats[calendar.unit === 'year' ? 'year' : calendar.unit === 'month' ? 'month' : 'day'].format(time);
      group.append(element('text', {x: 0, y: height - 17, 'text-anchor': 'middle'}, text));
      ticks.append(group);
    }
    const years = document.querySelector('#timeline-years'); years.replaceChildren();
    const start = new Date(view[0]).getUTCFullYear(), end = new Date(view[1]).getUTCFullYear();
    if (width < 500 && start !== end) {years.append(element('text', {x: padding, y: 27}, `${start}–${end}`)); return;}
    let lastYearEnd = -Infinity;
    for (let year = start; year <= end; year++) {
      const startX = Math.max(padding, x(Date.UTC(year, 0, 1)));
      if (startX > width - 64 || startX < lastYearEnd + 16) continue;
      lastYearEnd = startX + 44;
      years.append(element('text', {x: startX, y: 27}, String(year)));
    }
  }
  const overview = document.querySelector('#timeline-overview');
  const overviewPoints = document.querySelector('#timeline-overview-points');
  const brushWindow = document.querySelector('#timeline-overview-window');
  const brushHit = document.querySelector('#timeline-overview-window-hit');
  const brushStart = document.querySelector('#timeline-overview-start'), brushEnd = document.querySelector('#timeline-overview-end');
  const miniNodes = nodes.map(item => {
    const dot = element('circle', {r: 1.6, 'data-model': item.model.model, 'data-vendor': item.model.vendor, 'data-date': item.model.release_date});
    overviewPoints.append(dot); return {item, dot};
  });
  let miniKey = '', miniGesture = null;
  function overviewX(time) {return padding + (time - full[0]) / fullSpan * (width - 2 * padding);}
  function overviewTime(pixel) {return full[0] + (pixel - padding) / Math.max(1, width - 2 * padding) * fullSpan;}
  function drawOverview() {
    overview.setAttribute('viewBox', `0 0 ${width} 98`);
    const key = `${width.toFixed(2)}:${filterVersion}`;
    if (miniKey !== key) {
      miniKey = key;
      const offsets = [0, -5, 5, -10, 10, -15, 15, -20, 20], occupied = offsets.map(() => -Infinity);
      for (const {item, dot} of miniNodes) {
        const position = overviewX(item.time);
        let lane = occupied.findIndex(last => position - last >= 4);
        if (lane < 0) lane = occupied.indexOf(Math.min(...occupied));
        occupied[lane] = position;
        dot.setAttribute('cx', position); dot.setAttribute('cy', 36 + offsets[lane]);
        dot.dataset.selected = String(matches(item.model));
      }
      const years = document.querySelector('#timeline-overview-years'); years.replaceChildren();
      const first = new Date(full[0]).getUTCFullYear(), last = new Date(full[1]).getUTCFullYear();
      const step = Math.max(1, Math.ceil((last - first) / Math.max(1, Math.floor((width - 2 * padding) / 75))));
      for (let year = first; year <= last; year++) {
        if (year !== first && year !== last && year % step !== 0) continue;
        const position = Math.max(padding, overviewX(Date.UTC(year, 0, 1)));
        if (year === first && step > 1) continue;
        years.append(element('text', {x: position, y: 88, 'text-anchor': 'middle'}, String(year)));
      }
    }
    const start = overviewX(view[0]), end = overviewX(view[1]);
    brushWindow.setAttribute('x', start); brushWindow.setAttribute('width', Math.max(.5, end - start));
    const middle = (start + end) / 2, narrow = end - start < 24;
    brushHit.setAttribute('x', narrow ? middle - 12 : start); brushHit.setAttribute('width', Math.max(24, end - start));
    for (const [handle, position, value] of [[brushStart, narrow ? middle - 12 : start, view[0]], [brushEnd, narrow ? middle + 12 : end, view[1]]]) {
      handle.setAttribute('transform', `translate(${position},0)`);
      handle.setAttribute('aria-valuemin', handle === brushStart ? full[0] : Math.min(full[1], view[0] + minimumSpan));
      handle.setAttribute('aria-valuemax', handle === brushStart ? Math.max(full[0], view[1] - minimumSpan) : full[1]);
      handle.setAttribute('aria-valuenow', Math.round(value)); handle.setAttribute('aria-valuetext', dateText(value));
    }
    brushWindow.setAttribute('aria-valuemin', full[0]); brushWindow.setAttribute('aria-valuemax', full[1]);
    brushWindow.setAttribute('aria-valuenow', Math.round((view[0] + view[1]) / 2));
    brushWindow.setAttribute('aria-valuetext', `${dateText(view[0])} – ${dateText(view[1])}`);
    overview.dataset.from = dateText(view[0]); overview.dataset.to = dateText(view[1]);
  }
  overview.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    event.preventDefault(); interrupt(); hideTooltip();
    const pixel = event.clientX - overview.getBoundingClientRect().left;
    let mode = event.target.closest('[data-brush]')?.dataset.brush;
    if (!mode) {
      const span = Math.min(target[1] - target[0], 365 * day), centre = overviewTime(pixel);
      setWindow(centre - span / 2, centre + span / 2); mode = 'move';
    }
    miniGesture = {mode, start: [...target], x: event.clientX, pixel, moved: false, pointer: event.pointerId};
    overview.setPointerCapture(event.pointerId);
  });
  overview.addEventListener('pointermove', event => {
    if (!miniGesture || miniGesture.pointer !== event.pointerId) return;
    const movement = event.clientX - miniGesture.x;
    if (!miniGesture.moved && Math.abs(movement) < 3) return;
    miniGesture.moved = true;
    const shift = movement / Math.max(1, width - 2 * padding) * fullSpan, [start, end] = miniGesture.start;
    if (miniGesture.mode === 'start') setWindow(Math.max(full[0], Math.min(end - minimumSpan, start + shift)), end);
    else if (miniGesture.mode === 'end') setWindow(start, Math.min(full[1], Math.max(start + minimumSpan, end + shift)));
    else setWindow(start + shift, end + shift);
  });
  function endMiniGesture(event) {
    if (!miniGesture || miniGesture.pointer !== event.pointerId) return;
    if (event.type !== 'pointercancel' && !miniGesture.moved && miniGesture.mode === 'move' && isFull(miniGesture.start)) {
      const centre = overviewTime(miniGesture.pixel), span = Math.min(fullSpan, 365 * day);
      setWindow(centre - span / 2, centre + span / 2, true);
    }
    miniGesture = null;
    if (overview.hasPointerCapture(event.pointerId)) overview.releasePointerCapture(event.pointerId);
    if (urlTimer) persistURL();
    if (!section.getAttribute('aria-busy') || section.getAttribute('aria-busy') === 'false') settle();
  }
  overview.addEventListener('pointerup', endMiniGesture); overview.addEventListener('pointercancel', endMiniGesture);
  overview.addEventListener('dblclick', event => {event.preventDefault(); interrupt(); setWindow(...full, true);});
  overview.addEventListener('keydown', event => {
    const mode = event.target.closest('[data-brush]')?.dataset.brush;
    if (!mode || !['ArrowLeft', 'ArrowRight', 'Home', 'End', '+', '=', '-'].includes(event.key)) return;
    event.preventDefault(); interrupt();
    if (event.key === '+' || event.key === '=') {zoom(2); return;}
    if (event.key === '-') {zoom(.5); return;}
    const [start, end] = target, span = end - start, step = span * (event.shiftKey ? .4 : .1);
    const shift = event.key === 'ArrowLeft' ? -step : step;
    if (mode === 'start') {
      const value = event.key === 'Home' ? full[0] : event.key === 'End' ? end - minimumSpan : Math.max(full[0], Math.min(end - minimumSpan, start + shift));
      setWindow(value, end);
    } else if (mode === 'end') {
      const value = event.key === 'Home' ? start + minimumSpan : event.key === 'End' ? full[1] : Math.min(full[1], Math.max(start + minimumSpan, end + shift));
      setWindow(start, value);
    } else {
      const from = event.key === 'Home' ? full[0] : event.key === 'End' ? full[1] - span : start + shift;
      setWindow(from, from + span);
    }
  });
  function render() {
    if (width < 60) return;
    drawLayout();
    svg.dataset.from = dateText(view[0]); svg.dataset.to = dateText(view[1]);
    drawCalendar();
    const matching = nodes.filter(item => matches(item.model));
    const inView = item => matches(item.model) && item.time >= view[0] && item.time <= view[1];
    const visible = matching.filter(inView).length;
    for (const item of nodes) item.link.setAttribute('tabindex', inView(item) ? '0' : '-1');
    const focused = document.activeElement?.timelineItem;
    if (focused && !inView(focused)) svg.focus({preventScroll: true});
    const unconfirmed = undated.filter(matches).length, unconfirmedLabel = document.querySelector('#timeline-undated-count');
    unconfirmedLabel.hidden = unconfirmed === 0; unconfirmedLabel.textContent = `${unconfirmed} ${unconfirmedLabel.dataset.label}`;
    const empty = document.querySelector('#timeline-empty'); empty.toggleAttribute('hidden', visible !== 0);
    empty.setAttribute('x', width / 2); empty.setAttribute('y', axis - 24);
    document.querySelector('#timeline-visible-count').textContent = `${visible} / ${matching.length} ${section.dataset.countLabel}`;
    document.querySelector('#timeline-range').textContent = dated.length ? `${dateText(view[0])} – ${dateText(view[1])}` : '';
    const scale = fullSpan / (view[1] - view[0]);
    document.querySelector('#timeline-zoom').textContent = `${scale < 10 ? scale.toFixed(1).replace(/\.0$/, '') : Math.round(scale)}×`;
    document.querySelector('#timeline-out').disabled = view[1] - view[0] >= maximumSpan() * .999;
    document.querySelector('#timeline-in').disabled = view[1] - view[0] <= minimumSpan * 1.001;
    if (activeNode && (!matches(activeNode.model) || activeNode.time < view[0] || activeNode.time > view[1])) hideTooltip();
    else {positionTooltip(); if (activeNode) showGuide(activeNode.time);}
    drawOverview();
    const windowKey = `${view[0]}:${view[1]}`;
    if (lastWindow !== windowKey) {lastWindow = windowKey; explorer.setWindow(view[0], view[1], isFull(view));}
  }
  function isFull(range) {return range[0] <= full[0] + 1 && range[1] >= full[1] - 1;}
  function fittedRange() {
    const found = dated.filter(matches);
    if (!found.length) return constrain(full[1] - maximumSpan(), full[1]);
    const earliest = Math.min(...found.map(model => model.time)), latest = Math.max(...found.map(model => model.time));
    const extra = Math.max(3 * day, (latest - earliest) * .03), end = Math.min(full[1], latest + extra);
    return constrain(Math.max(earliest - extra, end - maximumSpan()), end);
  }
  function setPhase(value) {phase = value; section.dataset.phase = value; refreshScope();}
  function cancelFocus() {clearTimeout(focusTimer); focusGeneration++;}
  function interrupt() {cancelFocus(); cancelAnimationFrame(animation); clearTimeout(motionTimer); delete section.dataset.moving; target = [...view]; setPhase('idle'); section.setAttribute('aria-busy', 'false'); requestAnimationFrame(() => {if (!section.dataset.moving) render();});}
  function focusPublisher(context = true) {
    cancelFocus(); hideTooltip();
    const generation = focusGeneration;
    if (reducedMotion.matches || !context || !explorer.publisher()) {
      setPhase('idle'); setWindow(...fittedRange(), !reducedMotion.matches, 650); return;
    }
    setPhase('overview');
    const found = dated.filter(matches), latest = found.length ? Math.max(...found.map(model => model.time)) : full[1];
    setWindow(...full);
    focusTimer = setTimeout(() => {
      if (generation !== focusGeneration) return;
      setPhase('highlight'); render();
      focusTimer = setTimeout(() => {
        if (generation !== focusGeneration) return;
        setPhase('zoom'); setWindow(...fittedRange(), true, 780);
        focusTimer = setTimeout(() => {if (generation === focusGeneration) {setPhase('idle'); render();}}, 820);
      }, 340);
    }, 180);
  }
  for (const control of document.querySelectorAll('.timeline-controls button')) control.addEventListener('click', interrupt);
  document.querySelector('#timeline-in').addEventListener('click', () => zoom(2));
  document.querySelector('#timeline-out').addEventListener('click', () => zoom(.5));
  document.querySelector('#timeline-fit').addEventListener('click', () => setWindow(...fittedRange(), true));
  document.querySelector('#timeline-latest').addEventListener('click', () => {
    const found = dated.filter(matches), latest = found.length ? Math.max(...found.map(model => model.time)) : full[1];
    setWindow(latest - Math.min(120 * day, maximumSpan()), latest, true);
  });
  document.addEventListener('frontier:filters', event => {
    filterVersion++;
    if (event.detail.fit) focusPublisher(event.detail.publisherChanged);
    else {interrupt(); view = target = constrain(...target); render();}
  });
  window.frontierTimeline = {returnToPublishers: async () => {
    leavingForChooser = true; cancelFocus(); hideTooltip();
    setPhase('overview'); setWindow(...full, true, 380);
    if (!reducedMotion.matches) await new Promise(resolve => setTimeout(resolve, 400));
  }};
  refreshScope();
  const from = Date.parse(params.get('from') || ''), to = Date.parse(params.get('to') || '');
  view = target = Number.isFinite(from) && Number.isFinite(to) && from < to ? constrain(from, to) : fittedRange();
  render(); updateURL();
  addEventListener('pageshow', event => {
    if (!event.persisted) return;
    if (leavingForChooser) {leavingForChooser = false; focusPublisher(true);}
    else {setPhase('idle'); view = [...target]; render();}
  });
  requestAnimationFrame(() => requestAnimationFrame(() => {
    Promise.resolve(window.frontierArrival).then(() => {
      if (window.frontierEntry?.kind === 'models-enter') focusPublisher(true);
      else {setPhase('idle'); render();}
    });
  }));
  reducedMotion.addEventListener('change', () => {if (reducedMotion.matches) {interrupt(); setWindow(...target);}});
  addEventListener('pagehide', () => {
    cancelFocus(); cancelAnimationFrame(animation); clearTimeout(motionTimer); delete section.dataset.moving;
    miniGesture = gesture = null; pointers.clear(); svg.classList.remove('is-dragging');
    view = [...target]; if (urlTimer) persistURL();
  });
  frame.addEventListener('wheel', event => {
    if (event.ctrlKey || event.metaKey) {
      event.preventDefault(); interrupt(); zoom(Math.exp(-Math.max(-100, Math.min(100, event.deltaY)) * .012), event.clientX - frame.getBoundingClientRect().left, false);
    } else if (event.shiftKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) {
      event.preventDefault(); interrupt();
      const shift = (event.deltaX || event.deltaY) / Math.max(1, width - 2 * padding) * (target[1] - target[0]);
      setWindow(target[0] + shift, target[1] + shift);
    }
  }, {passive: false});
  svg.addEventListener('dragstart', event => event.preventDefault());
  svg.addEventListener('dblclick', event => {
    if (event.target.closest('a')) return;
    event.preventDefault(); interrupt(); zoom(event.shiftKey ? .5 : 2, event.clientX - frame.getBoundingClientRect().left);
  });
  svg.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    interrupt(); pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    const positions = [...pointers.values()];
    gesture = {start: [...target], x: event.clientX, y: event.clientY, moved: false,
      distance: positions.length === 2 ? Math.hypot(positions[1].x - positions[0].x, positions[1].y - positions[0].y) : 0,
      center: positions.length === 2 ? (positions[0].x + positions[1].x) / 2 - frame.getBoundingClientRect().left : 0};
  });
  svg.addEventListener('pointermove', event => {
    if (!gesture || !pointers.has(event.pointerId)) {
      if (!activeNode) hideGuide();
      return;
    }
    pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    const positions = [...pointers.values()];
    if (positions.length === 2 && gesture.distance > 0) {
      const distance = Math.max(1, Math.hypot(positions[1].x - positions[0].x, positions[1].y - positions[0].y));
      const center = (positions[0].x + positions[1].x) / 2 - frame.getBoundingClientRect().left;
      const ratio = (center - padding) / Math.max(1, width - 2 * padding), anchor = timeAt(gesture.center, gesture.start);
      const span = (gesture.start[1] - gesture.start[0]) * gesture.distance / distance;
      setWindow(anchor - ratio * span, anchor + (1 - ratio) * span); gesture.moved = true;
    } else {
      const movement = event.clientX - gesture.x;
      if (!gesture.moved && Math.abs(movement) < 5) return;
      if (!gesture.moved && event.pointerType === 'touch' && Math.abs(movement) < Math.abs(event.clientY - gesture.y)) return;
      gesture.moved = true;
      const shift = -movement / Math.max(1, width - 2 * padding) * (gesture.start[1] - gesture.start[0]);
      setWindow(gesture.start[0] + shift, gesture.start[1] + shift);
    }
    hideTooltip(); svg.classList.add('is-dragging'); svg.setPointerCapture(event.pointerId);
  });
  svg.addEventListener('pointerleave', () => {if (!activeNode) hideGuide();});
  function endGesture(event) {
    if (gesture?.moved) suppressClickUntil = performance.now() + 200;
    pointers.delete(event.pointerId); gesture = null; svg.classList.remove('is-dragging');
    if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId);
    if (urlTimer) persistURL();
  }
  svg.addEventListener('pointerup', endGesture); svg.addEventListener('pointercancel', endGesture);
  addEventListener('pointerup', event => {if (pointers.has(event.pointerId)) endGesture(event);});
  document.addEventListener('click', event => {if (urlTimer && event.target.closest('a[href]')) persistURL();}, true);
  svg.addEventListener('click', event => {if (event.detail > 0 && performance.now() < suppressClickUntil) event.preventDefault();}, true);
  svg.addEventListener('keydown', event => {
    if (event.key === 'Escape') {hideTooltip(); return;}
    if (!['+', '=', '-', 'Home', 'End', 'ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault(); interrupt();
    if (event.key === '+' || event.key === '=') zoom(2);
    else if (event.key === '-') zoom(.5);
    else if (event.key === 'Home') setWindow(full[0], full[0] + (target[1] - target[0]), true);
    else if (event.key === 'End') setWindow(full[1] - (target[1] - target[0]), full[1], true);
    else {
      const selected = nodes.findIndex(item => item.link === document.activeElement), direction = event.key === 'ArrowRight' ? 1 : -1;
      if (selected >= 0) {
        const item = direction > 0 ? nodes.slice(selected + 1).find(item => matches(item.model)) : nodes.slice(0, selected).reverse().find(item => matches(item.model));
        if (item) item.link.focus({preventScroll: true});
      } else {
        const shift = direction * (target[1] - target[0]) * .35; setWindow(target[0] + shift, target[1] + shift, true);
      }
    }
  });
  new ResizeObserver(() => {
    if (Math.abs(width - frame.clientWidth) < 1) return;
    width = frame.clientWidth; height = svg.clientHeight; refreshScope(); view = target = constrain(...target); render(); updateURL();
  }).observe(frame);
})();
