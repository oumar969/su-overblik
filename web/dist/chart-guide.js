/* Explain the same monthly rows that power the chart; no separate loan maths. */
'use strict';
(() => {
  const chart = document.getElementById('chart');
  const panel = document.createElement('section');
  panel.className = 'chart-guide';
  panel.setAttribute('aria-label', 'Udforsk grafen med Bo');
  panel.innerHTML = `
    <div class="chart-guide-heading"><img src="guide.png" width="56" height="56" alt="">
      <div><strong>Bo forklarer grafen</strong><p>Tryk på kurven, eller vælg en måned nedenfor.</p></div></div>
    <label for="chart-month">Vælg tidspunkt <output id="chart-month-label" for="chart-month"></output></label>
    <input id="chart-month" type="range" min="0" step="1" value="0">
    <div class="chart-guide-ends"><span id="chart-first"></span><span id="chart-last"></span></div>
    <div class="chart-explanation" role="status" aria-live="polite" aria-atomic="true">
      <h3 id="chart-phase"></h3><p id="chart-balance"></p><p id="chart-story"></p><p id="chart-fee"></p>
    </div>`;
  chart.after(panel);
  const slider = document.getElementById('chart-month');
  const set = (id, value) => { document.getElementById(id).textContent = value.replace(/kr\.\./g, 'kr.'); };
  let scenario, rows = [], selectedMonth;
  function select(index) {
    index = Math.max(0, Math.min(rows.length - 1, index));
    const row = rows[index];
    selectedMonth = row.month;
    slider.value = String(index);
    slider.setAttribute('aria-valuetext', date(row.month));
    set('chart-month-label', date(row.month));
    const previous = index ? rows[index - 1].debt : Number(scenario.input.debt) * 100;
    const change = row.debt - previous;
    const movement = change > 0 ? `Gælden stiger med ${exact(change)}.` : change < 0 ? `Gælden falder med ${exact(-change)}.` : 'Gælden er uændret denne måned.';
    const studying = index < scenario.study.rows.length;
    let phase, story;
    if (studying) {
      const loan = Number(scenario.input.loan) * 100;
      phase = 'Under studiet';
      story = `${movement} Du låner ${exact(loan)}, og der lægges ${exact(row.interest)} i renter til. Renten beregnes også af tidligere tilskrevne renter.`;
    } else if (row.payment) {
      phase = row.debt === 0 ? 'Den sidste betaling' : 'Du betaler tilbage';
      story = `${movement} Der lægges ${exact(row.interest)} i renter til, og du betaler ${exact(row.payment)} på gælden.${row.debt === 0 ? ' Nu er lånet betalt i dette scenarie.' : ''}`;
    } else if (scenario.payment.start && row.month < scenario.payment.start) {
      phase = 'Ventetid før første betaling';
      story = `${movement} Du låner ikke mere og betaler endnu ikke af. Der lægges ${exact(row.interest)} i renter til.${row.interest ? ' Derfor kan gælden vokse efter studiet.' : ' Med den valgte rente vokser gælden ikke denne måned.'}`;
    } else {
      phase = row.debt === 0 ? 'Ingen gæld' : 'Mellem betalingerne';
      story = row.debt === 0 ? 'Der er ingen gæld, renter eller betalinger denne måned.' : `${movement} Du har ingen betaling denne måned, men der lægges ${exact(row.interest)} i renter til. Du betaler hver anden måned i denne plan.`;
    }
    set('chart-phase', `${date(row.month)} · ${phase}`);
    set('chart-balance', `Gæld ved månedens slutning: ${exact(row.debt)}`);
    set('chart-story', story);
    set('chart-fee', row.fee ? `Du betaler også ${exact(row.fee)} i gebyr. Samlet opkrævning: ${exact(row.payment + row.fee)}. Gebyret lægges ikke til gælden på grafen.` : '');
    document.getElementById('chart-fee').hidden = !row.fee;
    const svg = chart.querySelector('svg');
    const point = svg.querySelector('polyline').points.getItem(index);
    let marker = svg.querySelector('.selected-month');
    if (!marker) {
      marker = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      marker.setAttribute('class', 'selected-month');
      marker.setAttribute('aria-hidden', 'true');
      marker.innerHTML = '<line stroke="#172339" stroke-dasharray="3 4"/><circle r="6" fill="#fff" stroke="#2745db" stroke-width="3"/>';
      svg.append(marker);
    }
    const line = marker.querySelector('line'), dot = marker.querySelector('circle');
    line.setAttribute('x1', point.x); line.setAttribute('x2', point.x);
    line.setAttribute('y1', 17); line.setAttribute('y2', 207);
    dot.setAttribute('cx', point.x); dot.setAttribute('cy', point.y);
  }
  function refresh(result) {
    scenario = result;
    rows = [...result.study.rows, ...result.payment.rows];
    slider.max = String(rows.length - 1);
    set('chart-first', date(rows[0].month));
    set('chart-last', date(rows.at(-1).month));
    const previousIndex = rows.findIndex(row => row.month === selectedMonth);
    select(previousIndex < 0 ? result.study.rows.length - 1 : previousIndex);
  }
  slider.addEventListener('input', () => select(Number(slider.value)));
  chart.addEventListener('click', event => {
    const svg = chart.querySelector('svg');
    const matrix = svg.getScreenCTM();
    if (!matrix) return;
    const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
    const points = svg.querySelector('polyline').points;
    let nearest = 0, distance = Infinity;
    for (let index = 0; index < points.numberOfItems; index++) {
      const delta = Math.abs(points.getItem(index).x - point.x);
      if (delta < distance) { nearest = index; distance = delta; }
    }
    select(nearest);
  });
  document.addEventListener('su:calculated', event => refresh(event.detail));
  refresh(current);
})();
