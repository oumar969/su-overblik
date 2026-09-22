"""Compare every monthly browser result with Python; run from any directory."""
import json
import random
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

from su_beregner import beregn
from tilbagebetaling import tilbagebetal

ROOT = Path(__file__).resolve().parent


def scenarios():
    yield (2000, 0, '2026-09', '2029-06', '2.85', 2)
    yield (0, 0, '2026-01', '2026-12', '0', 2)
    yield (0, 10, '2026-01', '2026-01', '0', 1)
    yield (3799, 40000, '2026-09', '2030-06', '4.5', 1)
    yield (1500, 5000, '2026-12', '2027-01', '12', 2)
    rng = random.Random(42)
    for _ in range(200):
        first = 2026 * 12 + rng.randrange(12)
        last = first + rng.randrange(600)
        date = lambda value: f'{value // 12:04d}-{value % 12 + 1:02d}'
        yield (str(Decimal(rng.randrange(379901)) / 100),
               str(Decimal(rng.randrange(100000001)) / 100),
               date(first), date(last),
               str(Decimal(rng.randrange(10001)) / 100), rng.choice((1, 2)))


def reference(case):
    loan, debt, start, end, rate, interval = case
    study = beregn(debt, loan, start, end)
    plan = tilbagebetal(study[-1]['gaeld'], end, rate, interval)
    cents = lambda value: int(value * 100)
    study_rows = [dict(month=r['maaned'], debt=cents(r['gaeld']),
                       interest=cents(r['renter']), payment=0, fee=0) for r in study]
    payment_rows = [dict(month=r['maaned'], debt=cents(r['gaeld']),
                         interest=cents(r['renter']), payment=cents(r['betaling']),
                         fee=cents(r['gebyr'])) for r in plan['rows']]
    return dict(input=dict(loan=loan, debt=debt, start=start, end=end, rate=rate, interval=interval),
                expected=dict(study=study_rows, payment=payment_rows,
                              total=cents(plan['samlet_betaling']), end=plan['slut']))


def main():
    node = shutil.which('node')
    if node is None:
        bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
        if not bundled.is_file():
            raise SystemExit('Node.js mangler. Installer Node.js og kør kontrollen igen.')
        node = str(bundled)
    script = r"""
const {calculate} = require('./web/dist/calculator.js');
const assert = require('node:assert/strict');
let text = '';
process.stdin.on('data', chunk => text += chunk);
process.stdin.on('end', () => {
    const cases = JSON.parse(text);
    for (const [index, test] of cases.entries()) {
        const result = calculate(test.input);
        const actual = {study: result.study.rows, payment: result.payment.rows,
                        total: result.payment.total, end: result.payment.end};
        try { assert.deepEqual(actual, test.expected); }
        catch (error) {
            console.error('Failed scenario', index, JSON.stringify(test.input));
            throw error;
        }
    }
    console.log(`${cases.length} web/Python comparisons passed, including every monthly row.`);
});
"""
    subprocess.run([node, '-e', script], cwd=ROOT,
                   input=json.dumps([reference(case) for case in scenarios()]),
                   text=True, check=True)


if __name__ == '__main__':
    main()
