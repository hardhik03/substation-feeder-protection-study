import os
import sys
import math
import opendssdirect as dss

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

STUDY_BUS = { 'SubstationBus':13.8, '650': 4.16, '632': 4.16, '671': 4.16, '675': 4.16, '652': 4.16}

SBASE_MVA = 10.0  # Base MVA for per-unit calculations

def calc_ibase(vbase_kv, sbase_mva):
    """Calculate the base current in amperes for a given voltage and power base."""
    return (sbase_mva * 1e6) / (math.sqrt(3) * vbase_kv * 1e3)

def run_fault_study():
    os.chdir(MODELS_DIR)
    dss.Text.Command('Compile master_combined.dss')
    dss.Text.Command('Solve mode=snapshot')

    results = {}

    for bus, vbase_kv in STUDY_BUS.items():
        # Set active bus first, then run fault study at that bus
        dss.Circuit.SetActiveBus(bus)
        dss.Text.Command(f'Solve mode=faultstudy')
        
        isc = dss.Bus.Isc()
        ibase = calc_ibase(vbase_kv,SBASE_MVA)

        phases = []
        for i in range(0, len(isc), 2):
            magnitude = math.sqrt(isc[i]**2 + isc[i+1]**2)
            phases.append(round(magnitude, 1))

        avg_3ph = round(sum(phases) / len(phases), 1)

        results[bus] = {
            'vbase_kv':  vbase_kv,
            'ibase_a':   round(ibase, 1),
            'phases_a':  phases,
            'avg_3ph_a': avg_3ph,
            'fault_mva': round(math.sqrt(3) * vbase_kv * avg_3ph / 1000, 2)
        }

    return results

def print_results(results):
    print()
    print('=' * 65)
    print('SHORT CIRCUIT STUDY — Combined Substation + IEEE 13-Bus Feeder')
    print('=' * 65)
    print(f'{"Bus":<15} {"Vbase":>8} {"Ibase":>8} {"Ia":>8} {"Ib":>8} {"Ic":>8} {"Fault MVA":>10}')
    print(f'{"":.<15} {"(kV)":>8} {"(A)":>8} {"(A)":>8} {"(A)":>8} {"(A)":>8} {"(MVA)":>10}')
    print('-' * 65)

    for bus, data in results.items():
        phases = data['phases_a']
        # pad phases if single-phase bus
        ia = phases[0] if len(phases) > 0 else '-'
        ib = phases[1] if len(phases) > 1 else '-'
        ic = phases[2] if len(phases) > 2 else '-'

        print(f'{bus:<15} {data["vbase_kv"]:>8.2f} {data["ibase_a"]:>8.1f} '
              f'{ia:>8} {ib:>8} {ic:>8} {data["fault_mva"]:>10.2f}')

    print('=' * 65)
    print()
    print('Notes:')
    print('  - Fault current shown is 3-phase symmetrical (worst case for')
    print('    equipment sizing)')
    print('  - Fault MVA = √3 × Vbase × Iavg / 1000')
    print('  - Ibase calculated at Sbase = 10 MVA')
    print()


def save_results_csv(results):
    import csv
    output = os.path.join(RESULTS_DIR, 'short_circuit_results.csv')

    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Bus', 'Vbase_kV', 'Ibase_A',
                        'Ia_A', 'Ib_A', 'Ic_A',
                        'Avg3ph_A', 'FaultMVA'])

        for bus, data in results.items():
            phases = data['phases_a']
            ia = phases[0] if len(phases) > 0 else ''
            ib = phases[1] if len(phases) > 1 else ''
            ic = phases[2] if len(phases) > 2 else ''
            writer.writerow([
                bus,
                data['vbase_kv'],
                data['ibase_a'],
                ia, ib, ic,
                data['avg_3ph_a'],
                data['fault_mva']
            ])

    print(f'Results saved to: {output}')


if __name__ == '__main__':
    print('Running fault study...')
    results = run_fault_study()
    print_results(results)
    save_results_csv(results)