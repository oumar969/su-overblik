"""Local experiment tracking. Does not replace the published browser model."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

os.environ.setdefault('MLFLOW_ENABLE_TELEMETRY', 'false')
import mlflow
import numpy as np
from train_model import train

REPO = Path(__file__).resolve().parents[2]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(seed=42):
    root = REPO / '.artifacts'
    root.mkdir(exist_ok=True)
    mlflow.set_tracking_uri('sqlite:///' + (root / 'mlflow.db').as_posix())
    client = mlflow.MlflowClient()
    experiment = client.get_experiment_by_name('su-overblik-synthetic')
    experiment_id = experiment.experiment_id if experiment else client.create_experiment(
        'su-overblik-synthetic', artifact_location=(root / 'mlflow-artifacts').as_uri())
    with mlflow.start_run(experiment_id=experiment_id, run_name=f'ols-seed-{seed}') as active:
        output = root / 'runs' / active.info.run_id
        model = train(output, seed)
        dataset = output / 'dist' / 'simulerede-scenarier.csv'
        with dataset.open(encoding='utf-8-sig') as stream:
            rows = list(csv.DictReader(stream, delimiter=';'))
        train_ids = {r['scenario_id'] for r in rows if r['split'] == 'train'}
        test_ids = {r['scenario_id'] for r in rows if r['split'] == 'test'}
        if len(rows) != 5000 or len(train_ids) != 4000 or len(test_ids) != 1000 or train_ids & test_ids:
            raise ValueError('Invalid dataset split')
        metrics = model['metrics']
        passed = (all(np.isfinite(v) for v in metrics.values())
                  and metrics['mae'] < 150 and metrics['max_error'] < 1500
                  and metrics['mae'] < metrics['baseline_mae'])
        commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO, text=True).strip()
        dirty = bool(subprocess.check_output(['git','status','--porcelain'], cwd=REPO, text=True).strip())
        manifest = {'generator_version': 1, 'seed': seed, 'git_commit': commit, 'working_tree_dirty': dirty,
                    'dataset_sha256': digest(dataset), 'generator_sha256': digest(Path(__file__).with_name('train_model.py')),
                    'model_sha256': digest(output / 'ml' / 'evaluation.json'),
                    'python': platform.python_version(), 'numpy': np.__version__, 'mlflow': mlflow.__version__,
                    'quality_passed': passed, 'test_mae_limit_dkk': 150, 'test_max_error_limit_dkk': 1500,
                    'note': 'Synthetic calculator approximation. No tuning or model selection on the test set.'}
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        report = f"# SU ML experiment\n\nRun: {active.info.run_id}\n\nSynthetic scenarios: 5000; training: 4000; test: 1000.\n\n" + '\n'.join(f'- {k}: {v:.4f} DKK' for k,v in metrics.items()) + f'\n\nQuality gate: {passed}\n'
        (output / 'report.md').write_text(report, encoding='utf-8')
        mlflow.log_params({'seed':seed, 'samples':5000, 'train_count':4000, 'test_count':1000,
                           'algorithm':'OLS', 'feature_count':6, 'generator_version':1})
        mlflow.set_tags({'data_type':'synthetic', 'git_commit':commit, 'dataset_sha256':manifest['dataset_sha256'], 'quality_passed':str(passed)})
        mlflow.log_metrics(metrics)
        mlflow.log_artifacts(str(output))
        mlflow.log_artifact(__file__, 'source')
        mlflow.log_artifact(str(Path(__file__).with_name('train_model.py')), 'source')
        versions = subprocess.check_output([sys.executable,'-m','pip','freeze'], text=True)
        (output / 'environment.txt').write_text(versions, encoding='utf-8')
        mlflow.log_artifact(str(output / 'environment.txt'))
        if not passed:
            raise ValueError('Model failed documented quality limits; artifacts retained for inspection')
        print(f'MLflow run: {active.info.run_id}\nReport: {output / "report.md"}')
        return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    run(parser.parse_args().seed)
