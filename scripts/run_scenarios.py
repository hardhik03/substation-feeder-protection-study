"""
run_scenarios.py — Runs the full load flow analysis for each defined scenario
and produces a side-by-side comparison report.
"""

import os
import sys
import opendssdirect as dss
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
from scenarios import SCENARIOS

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

BUSES_TO_MONITOR = ['SubstationBus', '650', '632', '671', '675', '652']
ANSI_MIN = 0.95
ANSI_MAX = 1.05

def build_scenario_loadshape(load_multiplier, scenario_name):
    """Read the existing WACM loadshape and scale it by load_multiplier."""
    base_dss = os.path.join(MODELS_DIR, 'loadshape_wacm.dss')

    with open(base_dss, 'r') as f:
        content = f.read()

    # Extract the multiplier string from the existing loadshape
    import re
    match = re.search(r'mult=\(([^)]+)\)', content)
    if not match:
        raise ValueError('Could not parse multipliers from loadshape_wacm.dss')

    original_mults = [float(x) for x in match.group(1).split()]
    scaled_mults = [round(min(m * load_multiplier, 1.5), 4) for m in original_mults]

    # Write scenario-specific loadshape file
    mult_str = ' '.join(str(m) for m in scaled_mults)
    scenario_dss = os.path.join(MODELS_DIR, f'loadshape_{scenario_name}.dss')

    with open(scenario_dss, 'w') as f:
        f.write(f'! LoadShape for scenario: {scenario_name}\n')
        f.write(f'! Load multiplier: {load_multiplier}\n\n')
        f.write(f'New LoadShape.WACMProfile\n')
        f.write(f'~ npts=24\n')
        f.write(f'~ interval=1\n')
        f.write(f'~ mult=({mult_str})\n')
        f.write(f'~ useactual=no\n')

    return scenario_dss


def apply_t1_override(t1_kva):
    """Override T1 transformer rating in the compiled circuit."""
    dss.Text.Command(f'Edit Transformer.T1 kvas=[{t1_kva} {t1_kva}]')
    print(f'  T1 rating set to: {t1_kva} kVA')

def apply_phase_load_multipliers(phase_multipliers):
    """Scale individual loads by phase according to scenario config."""
    load_names = dss.Loads.AllNames()

    for load_name in load_names:
        dss.Loads.Name(load_name)

        # Access bus info through the CktElement interface
        dss.Circuit.SetActiveElement(f'Load.{load_name}')
        bus = dss.CktElement.BusNames()[0]
        phases = dss.Loads.Phases()

        # Determine which phase from bus name suffix
        phase = None
        if phases == 3:
            phase = None  # three-phase load — skip
        elif bus.endswith('.1'):
            phase = 1
        elif bus.endswith('.2'):
            phase = 2
        elif bus.endswith('.3'):
            phase = 3

        if phase and phase in phase_multipliers:
            multiplier = phase_multipliers[phase]
            current_kw = dss.Loads.kW()
            current_kvar = dss.Loads.kvar()
            dss.Loads.kW(current_kw * multiplier)
            dss.Loads.kvar(current_kvar * multiplier)

    print(f'  Phase multipliers applied: {phase_multipliers}')

def run_scenario(scenario_name, scenario_config):
    """Run 24-hour load flow for a single scenario."""
    print(f'\nRunning: {scenario_config["description"]}')

    # Build scenario-specific loadshape
    build_scenario_loadshape(1.0, scenario_name)

    # Write scenario master dss
    master_dss = os.path.join(MODELS_DIR, 'master_combined.dss')
    with open(master_dss, 'r') as f:
        content = f.read()

    scenario_content = content.replace(
        'Compile loadshape_wacm.dss',
        f'Compile loadshape_{scenario_name}.dss'
    )

    scenario_master = os.path.join(MODELS_DIR, f'master_{scenario_name}.dss')
    with open(scenario_master, 'w') as f:
        f.write(scenario_content)

    # Compile and initialize
    os.chdir(MODELS_DIR)
    dss.Text.Command('Clear')
    dss.Text.Command(f'Compile master_{scenario_name}.dss')
    dss.Text.Command('Solve mode=snapshot')

    # Apply scenario-specific overrides after compilation
    apply_t1_override(scenario_config['t1_kva'])
    apply_phase_load_multipliers(scenario_config['load_phase_multipliers'])

    # Switch to daily mode and solve
    dss.Text.Command('Set mode=daily stepsize=1h number=1')

    results = {bus: [] for bus in BUSES_TO_MONITOR}
    violations = []

    for hour in range(24):
        dss.Text.Command('Solve')

        for bus in BUSES_TO_MONITOR:
            dss.Circuit.SetActiveBus(bus)
            vmag = dss.Bus.puVmagAngle()[::2]
            avg_v = round(sum(vmag) / len(vmag), 4)
            results[bus].append(avg_v)

            if avg_v < ANSI_MIN or avg_v > ANSI_MAX:
                violations.append({
                    'bus': bus,
                    'hour': hour,
                    'voltage': avg_v
                })

    return results, violations

def plot_scenario_comparison(all_results):
    """Plot voltage profiles for all scenarios side by side."""
    hours = list(range(24))
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    scenario_names = list(all_results.keys())
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']

    for ax, scenario_name in zip(axes, scenario_names):
        results = all_results[scenario_name]['voltages']
        config = SCENARIOS[scenario_name]

        for i, bus in enumerate(BUSES_TO_MONITOR):
            ax.plot(hours, results[bus], color=colors[i],
                   marker='o', markersize=2, linewidth=1.5, label=bus)

        ax.axhline(y=ANSI_MAX, color='red', linestyle='--',
                  linewidth=1, alpha=0.7, label='ANSI Limits')
        ax.axhline(y=ANSI_MIN, color='red', linestyle='--',
                  linewidth=1, alpha=0.7)

        violations = all_results[scenario_name]['violations']
        title_suffix = f'\n[!] {len(violations)} ANSI violations' if violations else '\n[OK] No violations'

        ax.set_title(f'{scenario_name.replace("_", " ").title()}\n'
                    f'{config["description"]}{title_suffix}',
                    fontsize=9)
        ax.set_xlabel('Hour of Day')
        ax.set_ylim([0.90, 1.10])
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(0, 24, 4))

    axes[0].set_ylabel('Voltage (per-unit)')
    axes[0].legend(loc='lower left', fontsize=7)

    fig.suptitle('Scenario Comparison — 24-Hour Voltage Profile\n'
                'Combined Substation + IEEE 13-Bus Feeder\n'
                'ANSI C84.1 Range A Limits: 0.95–1.05 pu',
                fontsize=11)

    plt.tight_layout()
    output = os.path.join(RESULTS_DIR, 'scenario_comparison.png')
    plt.savefig(output, dpi=300)
    print(f'\nComparison plot saved to: {output}')


def print_scenario_summary(all_results):
    """Print a concise summary table across all scenarios."""
    print('\n' + '=' * 70)
    print('SCENARIO ANALYSIS SUMMARY')
    print('=' * 70)
    print(f'{"Scenario":<20} {"Min V (pu)":>12} {"Max V (pu)":>12} '
          f'{"Violations":>12} {"Status":>10}')
    print('-' * 70)

    for name, data in all_results.items():
        all_voltages = [v for bus_data in data['voltages'].values()
                       for v in bus_data]
        min_v = min(all_voltages)
        max_v = max(all_voltages)
        n_violations = len(data['violations'])
        status = 'PASS' if n_violations == 0 else 'FAIL'

        print(f'{name:<20} {min_v:>12.4f} {max_v:>12.4f} '
              f'{n_violations:>12} {status:>10}')

    print('=' * 70)

    # Print violation details if any
    for name, data in all_results.items():
        if data['violations']:
            print(f'\nViolations in {name}:')
            for v in data['violations']:
                print(f'  Bus {v["bus"]} Hour {v["hour"]:02d}: '
                      f'{v["voltage"]:.4f} pu')


if __name__ == '__main__':
    print('=' * 60)
    print('SCENARIO ANALYSIS — Three Operating Conditions')
    print('=' * 60)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_results = {}

    for scenario_name, scenario_config in SCENARIOS.items():
        voltages, violations = run_scenario(scenario_name, scenario_config)
        all_results[scenario_name] = {
            'voltages': voltages,
            'violations': violations,
        }
        status = 'PASS' if not violations else f'FAIL ({len(violations)} violations)'
        print(f'  → {status}')

    print_scenario_summary(all_results)
    plot_scenario_comparison(all_results)