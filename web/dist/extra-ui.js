'use strict';
(() => {
 const panel=document.createElement('section');panel.className='whatif-panel';
 panel.innerHTML=`<p class="eyebrow">SE DIN VEJ TIL GÆLDFRI</p><h2>Hvad gør et ekstra afdrag?</h2><p>Prøv en ekstra månedlig betaling fra første betalingsmåned. Vi bruger basisplanen fra Mit overblik, ikke rentescenarierne ovenfor.</p><label for="extra-payment">Ekstra pr. måned</label><output id="extra-value"></output><input id="extra-payment" type="range" min="0" max="2000" step="25" value="200"><button id="extra-goal" type="button">Find beløb til ét år tidligere</button><p id="extra-goal-status" role="status"></p><div id="extra-results" aria-live="polite"></div><p class="hint">Simulering: fast rente, uændrede ordinære betalinger og ekstra afdrag sidst på hver måned efter renter. Vi antager ingen ekstra gebyrer for ekstra indbetalinger. De almindelige gebyrer stopper, når gælden er betalt. Rentefradrag er ikke med. Din faktiske betalingsplan kan være anderledes.</p>`;
 document.getElementById('whatif').append(panel);
 const slider=document.getElementById('extra-payment'),result=document.getElementById('extra-results'),status=document.getElementById('extra-goal-status');
 const fmt=v=>new Intl.NumberFormat('da-DK',{style:'currency',currency:'DKK'}).format(v/100);
 const idx=m=>Number(m.slice(0,4))*12+Number(m.slice(5))-1;
 function draw(){
  if(!current)return;
  const r=SU_EXTRA.extraPayments(current.input,Number(slider.value));
  document.getElementById('extra-value').textContent=fmt(Number(slider.value)*100);
  if(!r.base.payment.end){result.innerHTML='<p>Der er ingen gæld at afdrage på i din nuværende plan.</p>';return;}
  const full=idx(r.base.payment.end)-idx(r.base.payment.start)+1,short=idx(r.end)-idx(r.base.payment.start)+1;
  result.innerHTML=`<div class="extra-stats"><p><strong>${r.monthsSaved} måneder</strong> tidligere gældfri</p><p><strong>${fmt(r.interestSaved)}</strong> færre renter</p><p><strong>${fmt(r.feesSaved)}</strong> færre gebyrer</p></div><p>Nuværende plan: gældfri ${r.base.payment.end}</p><div class="extra-track"><div style="width:100%"></div></div><p>Med ekstra afdrag: gældfri ${r.end}</p><div class="extra-track"><div style="width:${short/full*100}%;background:#176f65"></div></div><p>Planlagt månedlig reserve: <strong>${fmt(r.reserve)}</strong>, inklusive ekstra afdrag. Den sidste betaling begrænses til restgælden.</p>${r.budgetLeft===null?'<p class="hint">Tilføj indkomst og udgifter under Mit overblik for at se dit rådighedsbeløb med ekstra afdrag.</p>':`<p class="${r.budgetLeft<0?'wi-deficit':''}">Rådighedsbeløb med budgettet fra Mit overblik: <strong>${fmt(r.budgetLeft)}</strong>${r.budgetLeft<0?' – det valgte budget giver underskud.':''}</p>`}`;
 }
 slider.addEventListener('input',()=>{status.textContent='';draw();});
 document.getElementById('extra-goal').addEventListener('click',()=>{
  for(let amount=0;amount<=2000;amount+=25){if(SU_EXTRA.extraPayments(current.input,amount).monthsSaved>=12){slider.value=amount;draw();status.textContent=`Mindste beløb i trin på 25 kr. inden for skyderen: ${fmt(amount*100)} ekstra pr. måned.`;return;}}
  status.textContent='Målet kan ikke nås med op til 2.000 kr. ekstra pr. måned i dette scenarie.';
 });
 document.addEventListener('su:calculated',()=>{status.textContent='';draw();});draw();
})();
