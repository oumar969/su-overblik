/* Educational extra-payment scenario. Amounts and rows are integer ore. */
(function(root){
'use strict';
const calculate = typeof module !== 'undefined' ? require('./calculator.js').calculate : root.SU.calculate;
const index = m => Number(m.slice(0,4))*12+Number(m.slice(5))-1;
function extraPayments(input, monthly){
  if(typeof monthly!=='number'||!Number.isFinite(monthly)||monthly<0||monthly>2000||Math.abs(monthly*100-Math.round(monthly*100))>1e-6)throw Error('Ekstra betaling skal være 0–2.000 kr. med højst to decimaler.');
  const base=calculate(input), extra=Math.round(monthly*100), rows=[];
  let balance=base.study.debt;
  for(const original of base.payment.rows){
    if(balance===0)break;
    const interest=Math.round(balance*base.rate/1200+1e-7);balance+=interest;
    const active=base.payment.start && original.month>=base.payment.start;
    const regular=Math.min(original.payment,balance);balance-=regular;
    const additional=active?Math.min(extra,balance):0;balance-=additional;
    rows.push({month:original.month,interest,payment:regular+additional,extra:additional,fee:regular>0?original.fee:0,debt:balance});
  }
  const paid=rows.filter(r=>r.payment>0),end=paid.at(-1)?.month||null;
  const interest=rows.reduce((s,r)=>s+r.interest,0), fees=rows.reduce((s,r)=>s+r.fee,0);
  const reserve=base.payment.end?Math.ceil(base.payment.maxPayment/base.interval)+extra:0;
  return {base,rows,end,reserve,monthsSaved:end?index(base.payment.end)-index(end):0,
    interestSaved:base.payment.interest-interest,feesSaved:base.payment.fees-fees,
    budgetLeft:base.budget?base.budget.net-base.budget.expenses-reserve:null};
}
root.SU_EXTRA={extraPayments};if(typeof module!=='undefined')module.exports={extraPayments};
})(typeof globalThis!=='undefined'?globalThis:this);
