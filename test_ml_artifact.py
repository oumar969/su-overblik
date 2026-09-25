import csv, json, unittest
from pathlib import Path
import numpy as np
from su_beregner import beregn

class MLArtifactTests(unittest.TestCase):
    def test_artifact_and_holdout_metrics(self):
        model=json.loads(Path('web/ml/evaluation.json').read_text(encoding='utf-8'))
        with Path('web/dist/simulerede-scenarier.csv').open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f,delimiter=';'))
        train=[r for r in rows if r['split']=='train'];test=[r for r in rows if r['split']=='test']
        self.assertEqual((len(train),len(test)),(4000,1000))
        self.assertFalse(set(r['scenario_id'] for r in train)&set(r['scenario_id'] for r in test))
        errors=[]
        for row in test:
            loan=float(row['monthly_loan_dkk']);months=int(row['study_months']);initial=float(row['initial_debt_dkk'])
            x=np.array([loan,months,initial,loan*months,initial*months,loan*months*months])
            pred=max(0,model['coefficients'][0]+np.dot((x-model['means'])/model['scales'],model['coefficients'][1:]))
            errors.append(abs(pred-float(row['target_debt_dkk'])))
        self.assertAlmostEqual(float(np.mean(errors)),model['metrics']['mae'],places=8)
        for row in test[:10]:
            months=int(row['study_months']);end_index=2026*12+months-1
            end=f'{end_index//12:04d}-{end_index%12+1:02d}'
            actual=beregn(row['initial_debt_dkk'],row['monthly_loan_dkk'],'2026-01',end)[-1]['gaeld']
            self.assertEqual(float(actual),float(row['target_debt_dkk']))

class MLReproducibilityTests(unittest.TestCase):
    def test_training_is_reproducible_and_does_not_overwrite_release(self):
        import importlib.util
        import tempfile
        spec=importlib.util.spec_from_file_location('trainer', 'web/ml/train_model.py')
        trainer=importlib.util.module_from_spec(spec);spec.loader.exec_module(trainer)
        released=Path('web/dist/ml-model.js').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            first=Path(temp)/'first';second=Path(temp)/'second'
            a=trainer.train(first);b=trainer.train(second)
            self.assertEqual(a,b)
            self.assertEqual((first/'dist/simulerede-scenarier.csv').read_bytes(),(second/'dist/simulerede-scenarier.csv').read_bytes())
            self.assertAlmostEqual(a['metrics']['mae'],json.loads(Path('web/ml/evaluation.json').read_text(encoding='utf-8'))['metrics']['mae'],places=6)
        self.assertEqual(released,Path('web/dist/ml-model.js').read_bytes())
