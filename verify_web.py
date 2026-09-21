"""Compare browser calculations with the Python reference, without external packages."""
import json, subprocess, shutil, os
from pathlib import Path
from su_beregner import beregn
from tilbagebetaling import tilbagebetal
from decimal import Decimal

cases=[]
for loan,debt,start,end,rate,interval in [(2000,0,'2026-09','2029-06','2.85',2),(0,0,'2026-01','2026-12','0',2),(0,10,'2026-01','2026-01','0',1),(3799,40000,'2026-09','2030-06','4.5',1),(1500,5000,'2026-12','2027-01','12',2)]:
    study=beregn(debt,loan,start,end)
    plan=tilbagebetal(study[-1]['gaeld'],end,rate,interval)
    cases.append({'input':dict(loan=loan,debt=debt,start=start,end=end,rate=rate,interval=interval),'expected':{'debt':int(study[-1]['gaeld']*100),'total':int(plan['samlet_betaling']*100),'opening':int(plan['startgaeld']*100),'end':plan['slut']}})
node=shutil.which('node') or str(Path(os.environ['USERPROFILE'])/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
script="""const {calculate}=require('./web/dist/calculator.js');let text='';process.stdin.on('data',c=>text+=c);process.stdin.on('end',()=>{for(const c of JSON.parse(text)){const r=calculate(c.input);const actual={debt:r.study.debt,total:r.payment.total,opening:r.payment.opening,end:r.payment.end};require('assert').deepStrictEqual(actual,c.expected);}console.log('5 web/Python comparisons passed.');});"""
subprocess.run([node,'-e',script],input=json.dumps(cases),text=True,check=True)
