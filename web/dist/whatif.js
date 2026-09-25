/* Scenario analysis; no probabilities, forecasting or changes to the saved plan. */
'use strict';
(() => {
  const page = document.getElementById('whatif');
  page.innerHTML = `<div class="whatif-intro"><p class="eyebrow">PRØV DINE ANTAGELSER</p><h2>Hvor meget plads har du i budgettet?</h2><p>Tre faste rentescenarier. Ingen prognose eller sandsynligheder. Løn og udgifter ændrer budgettet, ikke gælden.</p></div>
  <div class="whatif-controls">
    <label>Rentestigning efter studiet <output id="wi-rise-value"></output><input id="wi-rise" type="range" min="0" max="5" step="0.25" value="2"><small>0 til 5 procentpoint oven i renten på din beregnede plan</small></label>
    <label>Leveomkostninger efter studiet <output id="wi-cost-value"></output><input id="wi-cost" type="range" min="0" max="40000" step="250" value="12000"><small>Pr. måned, uden betaling af SU-lånet</small></label>
    <label>Forventet nettoløn <output id="wi-income-value"></output><input id="wi-income" type="range" min="0" max="50000" step="250" value="22000"><small>Udbetalt efter skat pr. måned – din egen antagelse</small></label></div>
  <p id="wi-basis" class="hint"></p><p id="wi-error" role="status"></p>
  <div class="whatif-panel"><h2>Samme lån, tre renteforløb</h2><p class="hint">Studierenten er ens. Efter studiet holdes hver scenarierente fast gennem hele tilbagebetalingen.</p><div id="wi-chart"></div><div id="wi-legend" class="wi-legend"></div><div class="table-scroll"><table><caption>Scenarier og månedligt rådighedsbeløb</caption><thead><tr><th>Scenarie</th><th>Rente efter studiet</th><th>Reserve pr. måned</th><th>Rådighedsbeløb</th><th>Gældfri</th></tr></thead><tbody id="wi-table"></tbody></table></div></div>
  <div class="whatif-panel"><h2>Hvor går din nettoløn hen?</h2><label for="wi-selected">Vis budget for</label><select id="wi-selected"><option value="0">Basisrente</option><option value="1">Halv rentestigning</option><option value="2" selected>Fuld rentestigning</option></select><div id="wi-flow"></div><p class="hint">Reserven dækker den største lånebetaling fordelt pr. måned, inklusive gebyr. Rådighedsbeløbet er før ekstra opsparing og udgifter, du ikke har medtaget. Budgettet antages uændret efter studiet.</p></div>`;
  const el = id => document.getElementById('wi-' + id);
  const money = value => new Intl.NumberFormat('da-DK',{style:'currency',currency:'DKK',maximumFractionDigits:2}).format(value / 100);
  const names = ['Basisrente','Halv rentestigning','Fuld rentestigning'];
  const colors = ['#176f65','#2745db','#b35317'];
  const percent = n => new Intl.NumberFormat('da-DK',{maximumFractionDigits:3}).format(n) + ' %';
  const monthIndex = month => Number(month.slice(0,4))*12 + Number(month.slice(5))-1;
  function update() {
    if (!current) return;
    const rise = Number(el('rise').value), costs = Number(el('cost').value)*100, income = Number(el('income').value)*100;
    el('rise-value').textContent = percent(rise).replace(' %',' procentpoint');
    el('cost-value').textContent = money(costs); el('income-value').textContent = money(income);
    const base = Number(current.input.rate);
    el('basis').textContent = `Din senest beregnede plan: ${money(Number(current.input.loan)*100)} i lån pr. måned, ${current.start} til ${current.end}. Basisrente efter studiet: ${percent(base)}. Ændringer her påvirker ikke din oprindelige plan.`;
    let scenarios;
    try {
      scenarios = [0,0.5,1].map(factor => SU.calculate({...current.input, rate: Math.round((base+factor*rise)*100)/100,net:undefined,expenses:undefined}));
      el('error').textContent = '';
    } catch { el('error').textContent = 'Rentestigningen giver en rente uden for beregnerens interval (0–100 %). Sænk rentestigningen eller basisrenten.'; el('chart').replaceChildren();el('table').replaceChildren();el('legend').replaceChildren();el('flow').replaceChildren();return; }
    const lines = scenarios.map(s => [...s.study.rows,...s.payment.rows]);
    const start = monthIndex(current.start), finish = Math.max(...lines.map(rows=>monthIndex(rows.at(-1).month)));
    const maximum = Math.max(100,...lines.map(rows=>Math.max(...rows.map(r=>r.debt)))) * 1.08;
    const x = m => 72+(m-start)/Math.max(1,finish-start)*660, y = d => 240-d/maximum*210;
    let svg = '<svg viewBox="0 0 760 280" role="img" aria-label="Tre gældskurver på samme tidsakse. Nøjagtige budgettal findes i tabellen.">';
    for(let i=0;i<=3;i++){const v=maximum*i/3;svg+=`<line x1="72" x2="732" y1="${y(v)}" y2="${y(v)}" stroke="#dce2ec"/><text x="65" y="${y(v)+4}" text-anchor="end" font-size="11">${Math.round(v/100).toLocaleString('da-DK')}</text>`;}
    lines.forEach((rows,i)=>{
      const points=rows.map(r=>`${x(monthIndex(r.month))},${y(r.debt)}`);
      if(rows.at(-1).debt===0)points.push(`${x(finish)},${y(0)}`);
      svg+=`<polyline points="${points.join(' ')}" fill="none" stroke="${colors[i]}" stroke-width="3" stroke-dasharray="${['0','9 5','3 4'][i]}"/>`;
    });
    svg+=`<text x="72" y="265" font-size="12">${current.start}</text><text x="732" y="265" text-anchor="end" font-size="12">${Math.floor(finish/12)}-${String(finish%12+1).padStart(2,'0')}</text><text x="12" y="16" font-size="12">Gæld i kr.</text></svg>`;
    el('chart').innerHTML=svg;
    el('legend').innerHTML=names.map((name,i)=>`<span style="color:${colors[i]}">${['━','┄','┈'][i]} ${name} · ${percent(scenarios[i].rate)}</span>`).join('');
    el('table').innerHTML=scenarios.map((s,i)=>{const reserve=s.payment.maxPayment/s.interval,left=income-costs-reserve;return `<tr><th>${names[i]}</th><td>${percent(s.rate)}</td><td>${money(reserve)}</td><td class="${left<0?'negative':''}">${money(left)}</td><td>${s.payment.end || 'Ingen gæld'}</td></tr>`;}).join('');
    const s=scenarios[Number(el('selected').value)], reserve=s.payment.maxPayment/s.interval,left=income-costs-reserve;
    if(left<0){el('flow').innerHTML=`<div class="wi-deficit" role="status"><h3>Månedligt underskud: ${money(left)}</h3><p>Udgifter og reserve til SU-lånet overstiger din nettoløn med ${money(-left)}.</p><p>Nettoløn ${money(income)} − leveomkostninger ${money(costs)} − SU-reserve ${money(reserve)}.</p><p>Prøv at ændre dine antagelser. Der er intet positivt rådighedsbeløb i dette scenarie.</p></div>`;return;}
    if(income===0){el('flow').innerHTML='<p>Ingen indtægt eller udgifter i dette scenarie. Vælg en nettoløn for at vise pengestrømmen.</p>';return;}
    const amounts=[costs,reserve,left],labels=['Leveomkostninger','Reserve til SU','Rådighedsbeløb'];let offset=35;
    let flow=`<svg viewBox="0 0 760 340" role="img" aria-label="Nettoløn ${money(income)}, leveomkostninger ${money(costs)}, SU-reserve ${money(reserve)}, rådighedsbeløb ${money(left)}"><text x="12" y="20" font-size="15">Nettoløn: ${money(income)}</text><rect x="20" y="35" width="14" height="230" rx="4" fill="#172339"/>`;
    amounts.forEach((amount,i)=>{const h=amount/income*230,target=35+amounts.slice(0,i).reduce((a,b)=>a+b,0)/income*230+i*22; if(h>0){flow+=`<path d="M34 ${offset} C190 ${offset},250 ${target},420 ${target} L420 ${target+h} C250 ${target+h},190 ${offset+h},34 ${offset+h} Z" fill="${colors[i]}" opacity=".45"/><rect x="420" y="${target}" width="12" height="${h}" fill="${colors[i]}"/>`;}flow+=`<text x="450" y="${50+i*100}" font-size="14">${labels[i]}</text><text x="450" y="${73+i*100}" font-size="17" font-weight="700">${money(amount)}</text>`;offset+=h;});
    el('flow').innerHTML=flow+'</svg>';
  }
  page.addEventListener('input',update);document.addEventListener('su:calculated',update);update();
})();
