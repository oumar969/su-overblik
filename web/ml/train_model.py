"""Reproducible educational surrogate. Synthetic scenarios, not real borrowers."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv, json
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if HERE.name=='ml' else HERE/'ml-output'
FEATURES=['loan','months','initial','loan_months','initial_months','loan_months_squared']
def features(loan,months,initial):
    return [loan,months,initial,loan*months,initial*months,loan*months*months]
def target(loan,months,initial):
    debt=Decimal(str(initial))
    for _ in range(months):
        debt+=Decimal(str(loan))
        debt+=(debt/300).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
    return float(debt)
def train(output_root=None, seed=42):
    ROOT = Path(output_root) if output_root is not None else globals()["ROOT"]
    (ROOT/'dist').mkdir(parents=True,exist_ok=True)
    (ROOT/'ml').mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    rows=[]
    for i in range(5000):
        loan=int(rng.integers(0,3800)); months=int(rng.integers(1,85)); initial=int(rng.integers(0,100001))
        rows.append((loan,months,initial,target(loan,months,initial)))
    order=rng.permutation(len(rows)); train_ids=order[:4000]; test_ids=order[4000:]
    x=np.array([features(*r[:3]) for r in rows],dtype=float); y=np.array([r[3] for r in rows])
    # Preprocessing fitted on training data only; test split used once for reporting.
    mean=x[train_ids].mean(axis=0); scale=x[train_ids].std(axis=0)
    design=np.column_stack([np.ones(len(x)),(x-mean)/scale])
    coef=np.linalg.lstsq(design[train_ids],y[train_ids],rcond=None)[0]
    predicted=np.maximum(0,design[test_ids]@coef); errors=np.abs(predicted-y[test_ids])
    baseline=float(y[train_ids].mean())
    model={'label':'SIMULEREDE SCENARIER – IKKE PERSONDATA','seed':seed,'samples':5000,'train_count':4000,'test_count':1000,'method':'Lineær regression med seks inputfeatures, trænet med mindste kvadraters metode','target':'Gæld ved studieslut i kroner med fast 4 % studierente','features':FEATURES,'means':mean.tolist(),'scales':scale.tolist(),'coefficients':coef.tolist(),'ranges':{'loan':[0,3799],'months':[1,84],'initial':[0,100000]},'metrics':{'mae':float(errors.mean()),'rmse':float(np.sqrt(np.mean(errors**2))),'max_error':float(errors.max()),'baseline_mae':float(np.mean(np.abs(baseline-y[test_ids]))),'exact_mae':0},'limitations':['Simulerede og uafhængigt uniformt fordelte input er ikke repræsentative for studerende.','Resultatet måler efterligning af en beregner, ikke betalingsrisiko.','Den præcise beregner er facit og bør bruges i produktet.','Ingen modelvalg eller tuning på testdata. Ingen dokumentation for generalisering til virkelige personer.'],'sample_predictions':[{'actual':float(y[idx]),'predicted':float(max(0,design[idx]@coef))} for idx in test_ids[:20]]}
    (ROOT/'dist'/'ml-model.js').write_text('window.SU_MODEL = '+json.dumps(model,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    test_set=set(test_ids.tolist())
    with (ROOT/'dist'/'simulerede-scenarier.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['scenario_id','data_type','split','monthly_loan_dkk','study_months','initial_debt_dkk','target_debt_dkk'])
        for i,r in enumerate(rows):writer.writerow([i,'synthetic','test' if i in test_set else 'train',*r])
    (ROOT/'ml'/'evaluation.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(model['metrics'],indent=2))
    return model
if __name__=='__main__':train()
