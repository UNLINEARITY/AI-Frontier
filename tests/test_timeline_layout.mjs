import test from 'node:test';
import assert from 'node:assert/strict';
import '../site/timeline-layout.js';
const {wrapName, scatter, labelPositions, calendarTicks} = globalThis.frontierTimelineLayout;
const day = 86400000, date = value => Date.parse(`${value}T00:00:00Z`);
const measure = value => [...value].reduce((sum, letter) => sum + (/[^\x00-\xff]/.test(letter) ? 14 : 7), 0);
function model(name, time) {
  const lines = wrapName(name, measure);
  return {name, time, lines, textWidth: Math.max(...lines.map(measure))};
}
test('full long names survive wrapping, including CJK and unbroken identifiers', () => {
  for (const name of ['Nemotron Labs 3 Competitive Coding 550B-A55B', '完整模型名称应当直接显示且没有省略号', 'ExtremelyLongUnbrokenModelIdentifierThatMustNotBeTruncated']) {
    const lines = wrapName(name, measure, 112);
    assert.equal(lines.join('').replaceAll(' ', ''), name.replaceAll(' ', ''));
    assert.ok(lines.every(line => measure(line) <= 112));
  }
});
test('same-day variants keep identical x and elapsed UTC days keep their exact ratio', () => {
  const start = date('2024-02-28'), end = date('2024-03-03');
  const items = [model('A', start), model('A variant', start), model('Leap-day model', start + day), model('March model', start + 3 * day)];
  const [a, variant, leap, march] = scatter(items, [start, end], 1200, 400).items;
  assert.equal(a.x, variant.x); assert.notEqual(a.y, variant.y);
  assert.ok(Math.abs((march.x - a.x) / (leap.x - a.x) - 3) < 1e-9);
});
test('dense scatter stays compact without changing the number or dates of visible models', () => {
  const start = date('2026-01-01'), end = start + 180 * day;
  const items = Array.from({length: 240}, (_, index) => model(`Model ${index}`, start + Math.floor(index / 5) * day));
  const result = scatter(items, [start, end], 350, 350);
  assert.equal(result.items.length, 240);
  for (let i = 0; i < result.items.length; i++) {
    const a = result.items[i];
    assert.ok(a.x >= 28 && a.x <= 322 && a.y >= 58 && a.y <= 308);
    for (const b of result.items.slice(i + 1)) assert.ok(Math.hypot(a.x-b.x,a.y-b.y) >= a.radius+b.radius-0.01);
  }
});
test('progressive labels never overlap each other or model dots', () => {
  const start = date('2026-01-01'), end = start + 180 * day;
  const items = Array.from({length: 80}, (_, i) => model(`Complete model ${i} variant`, start + i * day));
  const packed = scatter(items, [start, end], 1000, 400), names = labelPositions(packed.items, 1000, 400);
  assert.ok(names.size > 0 && names.size < items.length);
  const boxes = [...names.values()];
  for(let i=0;i<boxes.length;i++) {
    const a=boxes[i]; assert.ok(a.left>=0 && a.right<=1000 && a.top>=58 && a.bottom<=358);
    for(const b of boxes.slice(i+1)) assert.ok(a.right<=b.left||a.left>=b.right||a.bottom<=b.top||a.top>=b.bottom);
    for(const point of packed.items) assert.ok(point.x+point.radius<=a.left||point.x-point.radius>=a.right||point.y+point.radius<=a.top||point.y-point.radius>=a.bottom);
  }
});
test('zoom exposes a higher fraction of complete names without expanding plot height', () => {
  const start = date('2026-01-01'), items=Array.from({length:100},(_,i)=>model(`Model ${i}`,start+i*day));
  const wide=scatter(items,[start,start+100*day],600,400), close=scatter(items,[start,start+5*day],600,400);
  const wideFraction=labelPositions(wide.items,600,400).size/wide.items.length;
  const closeFraction=labelPositions(close.items,600,400).size/close.items.length;
  assert.ok(closeFraction>wideFraction); assert.equal(closeFraction,1);
});
test('calendar months preserve leap-year spacing and weeks start on Monday', () => {
  const months=calendarTicks([date('2024-01-01'),date('2024-05-01')],500);
  assert.equal(months.unit,'month');assert.equal(months.dates[2]-months.dates[1],29*day);
  const weeks=calendarTicks([date('2026-01-01'),date('2026-02-01')],600);
  assert.equal(weeks.unit,'week');assert.ok(weeks.dates.every(time=>new Date(time).getUTCDay()===1));
});
