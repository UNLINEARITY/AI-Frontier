/* UTC positions stay proportional; point offsets and labels only manage density. */
(() => {
  const day = 86400000;
  function wrapName(name, measure, maximum = 196) {
    const lines = [];
    let remaining = name.trim();
    while (remaining) {
      if (measure(remaining) <= maximum) {lines.push(remaining); break;}
      const letters = [...remaining];
      let low = 1, high = letters.length;
      while (low < high) {
        const middle = Math.ceil((low + high) / 2);
        if (measure(letters.slice(0, middle).join('')) <= maximum) low = middle;
        else high = middle - 1;
      }
      const prefix = letters.slice(0, low).join('');
      const breaks = [...prefix.matchAll(/\s+|[-/]/g)];
      const last = breaks.at(-1);
      const cut = last && last.index > 0 ? last.index + last[0].length : prefix.length;
      lines.push(remaining.slice(0, cut).trim()); remaining = remaining.slice(cut).trimStart();
    }
    return lines;
  }
  function scatter(items, range, width, height, padding = 28) {
    const axis = (height + 20) / 2, limit = Math.min(axis - 72, height - 52 - axis);
    const visible = items.filter(item => item.time >= range[0] && item.time <= range[1]).sort((a, b) => a.time - b.time);
    let result = [];
    for (const radius of [4.5, 3.7, 3, 2.4, 1.8, 1.2]) {
      result = [];
      let fits = true;
      const gap = radius * 2 + 1.5;
      for (const item of visible) {
        const x = padding + (item.time - range[0]) / (range[1] - range[0]) * (width - 2 * padding);
        const forbidden = [];
        for (let i = result.length - 1; i >= 0 && x - result[i].x < gap; i--) {
          const other = result[i], dx = x - other.x;
          const distance = Math.sqrt(Math.max(0, gap * gap - dx * dx));
          forbidden.push([other.offset - distance, other.offset + distance]);
        }
        forbidden.sort((a, b) => a[0] - b[0]);
        const joined = [];
        for (const interval of forbidden) {
          if (joined.length && interval[0] <= joined.at(-1)[1] + .2) joined.at(-1)[1] = Math.max(joined.at(-1)[1], interval[1]);
          else joined.push([...interval]);
        }
        const centre = joined.find(interval => interval[0] <= 0 && interval[1] >= 0);
        let offset = 0;
        if (centre) {
          const choices = [centre[0] - .25, centre[1] + .25].filter(value => Math.abs(value) <= limit);
          choices.sort((a, b) => Math.abs(a) - Math.abs(b));
          if (!choices.length) {fits = false; break;}
          offset = choices[0];
        }
        result.push({...item, x, y: axis + offset, offset, radius});
      }
      if (fits) return {items: result, axis, radius};
    }
    // Extreme simultaneous launches may overlap as points, without falsifying x dates.
    return {items: visible.map((item, i) => ({...item, x: padding + (item.time - range[0]) / (range[1] - range[0]) * (width - 2 * padding), y: axis + ((i % 31) - 15) * (limit / 15), radius: 1.2})), axis, radius: 1.2};
  }
  function labelPositions(items, width, height) {
    const boxes = [], labels = new Map();
    // Distribute names across time instead of preferring a publisher or a flagship tier.
    const order = [];
    function visit(start, end) {
      if (start > end) return;
      const middle = Math.floor((start + end) / 2);
      order.push(items[middle]); visit(start, middle - 1); visit(middle + 1, end);
    }
    if (items.length) {order.push(items.at(-1)); if (items.length > 1) order.push(items[0]); visit(1, items.length - 2);}
    for (const item of order) {
      const w = item.textWidth, h = item.lines.length * 18;
      const candidates = [[item.x + 12, item.y - h / 2], [item.x - w - 12, item.y - h / 2],
        [Math.max(12, Math.min(width - w - 12, item.x - w / 2)), item.y - item.radius - 9 - h],
        [Math.max(12, Math.min(width - w - 12, item.x - w / 2)), item.y + item.radius + 9]];
      for (const [left, top] of candidates) {
        const box = {left, top, right: left + w, bottom: top + h};
        if (left < 10 || box.right > width - 10 || top < 58 || box.bottom > height - 42) continue;
        if (boxes.some(b => left < b.right + 7 && box.right + 7 > b.left && top < b.bottom + 5 && box.bottom + 5 > b.top)) continue;
        if (items.some(other => other.x + other.radius + 3 > left && other.x - other.radius - 3 < box.right && other.y + other.radius + 3 > top && other.y - other.radius - 3 < box.bottom)) continue;
        boxes.push(box); labels.set(item.link || item.name, box); break;
      }
    }
    return labels;
  }
  function calendarTicks(range, width) {
    const span = range[1] - range[0], desired = span / Math.max(2, Math.floor(width / 85));
    const choices = [['day', 1, day], ['day', 2, day * 2], ['week', 1, day * 7], ['week', 2, day * 14],
      ['month', 1, day * 30.44], ['month', 2, day * 60.88], ['month', 3, day * 91.32],
      ['month', 6, day * 182.64], ['year', 1, day * 365.25], ['year', 2, day * 730.5], ['year', 5, day * 1826.25]];
    const [unit, step] = choices.reduce((best, choice) => Math.abs(Math.log(choice[2] / desired)) < Math.abs(Math.log(best[2] / desired)) ? choice : best);
    const dates = [], start = new Date(range[0]);
    if (unit === 'month' || unit === 'year') {
      const months = unit === 'year' ? step * 12 : step;
      let month = Math.ceil((start.getUTCFullYear() * 12 + start.getUTCMonth()) / months) * months;
      for (let time; (time = Date.UTC(Math.floor(month / 12), month % 12, 1)) <= range[1]; month += months) if (time >= range[0]) dates.push(time);
    } else {
      const interval = day * step * (unit === 'week' ? 7 : 1);
      // Monday-aligned weeks; month lengths and leap years remain actual calendar time.
      const origin = unit === 'week' ? Date.UTC(1970, 0, 5) : 0;
      for (let time = origin + Math.ceil((range[0] - origin) / interval) * interval; time <= range[1]; time += interval) dates.push(time);
    }
    return {unit, step, dates};
  }
  globalThis.frontierTimelineLayout = {wrapName, scatter, labelPositions, calendarTicks};
})();
