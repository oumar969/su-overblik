const test=require('node:test'),assert=require('node:assert/strict');
const {extraPayments}=require('../dist/extra-payments.js');
const input={loan:2000,debt:0,start:'2026-09',end:'2029-06',rate:2.85,interval:2};
test('zero extra exactly reproduces regular payments and interest',()=>{
 for(const interval of [1,2])for(const rate of [0,2.85,10]){
  const r=extraPayments({...input,interval,rate},0);
  assert.equal(r.end,r.base.payment.end);assert.equal(r.interestSaved,0);assert.equal(r.feesSaved,0);
  assert.deepEqual(r.rows.map(({extra,...row})=>row),r.base.payment.rows);
 }
});
test('extra payments conserve money, cap final payment and start after grace period',()=>{
 let previous=0;
 for(const amount of [25,200,500,2000]){
  const r=extraPayments(input,amount);assert.ok(r.monthsSaved>=previous);previous=r.monthsSaved;
  assert.ok(r.interestSaved>0);assert.ok(r.feesSaved>=0);assert.equal(r.rows.at(-1).debt,0);
  let debt=r.base.study.debt;
  for(const row of r.rows){assert.equal(debt+row.interest-row.payment,row.debt);assert.ok(row.debt>=0);assert.ok(row.extra<=amount*100);if(row.month<r.base.payment.start)assert.equal(row.extra,0);debt=row.debt;}
 }
});
test('zero debt, invalid amounts and budget impact',()=>{
 assert.equal(extraPayments({...input,loan:0},200).end,null);
 for(const amount of [-1,2001,NaN,true,0.001])assert.throws(()=>extraPayments(input,amount));
 const r=extraPayments({...input,net:1000,expenses:900},200);
 assert.equal(r.budgetLeft,10000-r.reserve);assert.ok(r.budgetLeft<0);
});
