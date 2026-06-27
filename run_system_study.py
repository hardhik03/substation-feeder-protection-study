"""
run_system_study.py — Single entry point for the full analysis pipeline.

Usage:
    python run_system_study.py

Runs in order:
    1. Config validation
    2. EIA data fetch + LoadShape generation
    3. Regression test
    4. 24-hour load flow
    5. Short circuit study
    6. Protection coordination + TCC plot
"""

import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(BASE, 'scripts')


def run(label, script):
    print(f'\n{"=" * 60}')
    print(f'STEP: {label}')
    print('=' * 60)
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        cwd=BASE
    )
    if result.returncode != 0:
        print(f'\nPIPELINE FAILED at: {label}')
        print('Fix the issue above before re-running.')
        sys.exit(1)


if __name__ == '__main__':
    print('=' * 60)
    print('SUBSTATION + IEEE 13-BUS FEEDER PROTECTION STUDY')
    print('Full Analysis Pipeline')
    print('=' * 60)

    run('1. Config Validation',           'validate_config.py')
    run('2. EIA Data Fetch + LoadShape',  'build_loaddemand.py')
    run('3. Regression Test',             'regression_test.py')
    run('4. 24-Hour Load Flow',           'run_loadflow.py')
    run('5. Short Circuit Study',         'run_short_circuit.py')
    run('6. Protection Coordination',     'run_protection_coordination.py')

    print('\n' + '=' * 60)
    print('PIPELINE COMPLETE')
    print('Results saved to: results/')
    print('=' * 60)