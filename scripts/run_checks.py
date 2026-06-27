import subprocess
import sys
import os

base = os.path.dirname(os.path.abspath(__file__))

checks = [
    ('Config Validation', [sys.executable, os.path.join(base, 'validate_config.py')]),
    ('Regression Test',   [sys.executable, os.path.join(base, 'regression_test.py')]),
]

all_passed = True

for name, cmd in checks:
    print(f'Running {name}...')
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip())
        all_passed = False
    print()

if all_passed:
    print('ALL CHECKS PASSED — safe to proceed')
    sys.exit(0)
else:
    print('CHECKS FAILED — do not proceed until fixed')
    sys.exit(1)