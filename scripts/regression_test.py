import sys
import os
import opendssdirect as dss

# ── Configuration ─────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
TOLERANCE = 0.005  # 0.5% tolerance on per-unit voltage

# ── Known-good reference values from Phase 4 validation ───────────
# Format: bus_name -> [min_pu, max_pu] across all phases
REFERENCE = {
    'SubstationBus': [0.972, 0.992],
    '650':           [0.950, 0.978],
    '632':           [0.992, 1.037],
    '671':           [0.953, 1.048],
    '675':           [0.945, 1.051],
    '652':           [0.964, 0.975],
}

def run_regression():
    os.chdir(MODELS_DIR)
    dss.Text.Command('Compile master_combined.dss')

    if not dss.Solution.Converged():
        print('FAIL: Solution did not converge')
        sys.exit(1)

    failures = []

    for bus, (expected_min, expected_max) in REFERENCE.items():
        dss.Circuit.SetActiveBus(bus)
        voltages = dss.Bus.puVmagAngle()[::2]

        for i, v in enumerate(voltages):
            if v < (expected_min - TOLERANCE) or v > (expected_max + TOLERANCE):
                failures.append(
                    f'Bus {bus} phase {i+1}: {v:.4f} pu '
                    f'outside expected range '
                    f'[{expected_min-TOLERANCE:.4f}, '
                    f'{expected_max+TOLERANCE:.4f}]'
                )

    if failures:
        print('REGRESSION TEST FAILED:')
        for f in failures:
            print(f'  ✗ {f}')
        sys.exit(1)
    else:
        print('REGRESSION TEST PASSED')
        print(f'All {len(REFERENCE)} buses within tolerance')
        sys.exit(0)

if __name__ == '__main__':
    run_regression()