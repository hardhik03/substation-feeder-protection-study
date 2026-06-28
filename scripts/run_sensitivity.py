"""
run_sensitivity.py: Sensitivity sweep analysis of bridging transformer %Z
versus Bus 650 voltage, fault current, and CB2 trip time.

Sweeps BRIDGE_PCT_Z from 3.0% to 9.0% in 0.5% steps.
All other parameters held constant per config/system_parameters.py.

Reference: IEEE C57.12.36-2017 specifies 5.75% for this transformer
class — the sweep shows system sensitivity around that design point.
"""

import os
import sys
import math
import opendssdirect as dss
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
from system_parameters import BRIDGE_PCT_R, BRIDGE_PCT_Z

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# Sweep range
Z_MIN  = 3.0
Z_MAX  = 9.0
Z_STEP = 0.5
PCT_R  = BRIDGE_PCT_R  # held constant throughout sweep

# Protection settings (from Phase 6)
CB2_IP = 1560   # pickup current (A)
CB2_TD = 0.2    # time dial
A = 0.0515      # IEEE C37.112 moderately inverse constants
B = 0.1140
P = 0.02

# Design point from config
DESIGN_PCT_Z = BRIDGE_PCT_Z

def calc_xhl(pct_z, pct_r):
    """Calculate XHL from %Z and %R using impedance triangle."""
    return round(math.sqrt(pct_z**2 - pct_r**2), 4)


def cb2_trip_time(fault_current_a):
    """Calculate CB2 trip time per IEEE C37.112 moderately inverse curve."""
    if fault_current_a <= CB2_IP:
        return float('inf')
    return CB2_TD * (A / ((fault_current_a / CB2_IP)**P - 1) + B)


def run_sweep():
    """Sweep bridge transformer %Z and record system response."""
    z_values = list(np.arange(Z_MIN, Z_MAX + Z_STEP/2, Z_STEP))

    results = {
        'z_pct':        [],
        'xhl':          [],
        'bus650_v_pu':  [],
        'fault_i_a':    [],
        'cb2_trip_s':   [],
    }

    os.chdir(MODELS_DIR)

    for z_pct in z_values:
        xhl = calc_xhl(z_pct, PCT_R)

        # Compile fresh each iteration
        dss.Text.Command('Clear')
        dss.Text.Command('Compile master_combined.dss')
        dss.Text.Command('Solve mode=snapshot')

        # Override bridge transformer impedance
        dss.Text.Command(f'Edit Transformer.Bridge XHL={xhl} '
                        f'wdg=1 %r={PCT_R} wdg=2 %r={PCT_R}')

        # Re-solve after edit
        dss.Text.Command('Solve mode=snapshot')

        # Record Bus 650 voltage
        dss.Circuit.SetActiveBus('650')
        vmag = dss.Bus.puVmagAngle()[::2]
        avg_v = round(sum(vmag) / len(vmag), 4)

        # Record fault current at Bus 650
        dss.Circuit.SetActiveBus('650')
        dss.Text.Command('Solve mode=faultstudy')
        isc = dss.Bus.Isc()
        phases = []
        for i in range(0, len(isc), 2):
            phases.append(math.sqrt(isc[i]**2 + isc[i+1]**2))
        avg_fault = round(sum(phases) / len(phases), 1)

        # Record CB2 trip time at that fault current
        trip_t = round(cb2_trip_time(avg_fault), 4)

        results['z_pct'].append(round(z_pct, 1))
        results['xhl'].append(xhl)
        results['bus650_v_pu'].append(avg_v)
        results['fault_i_a'].append(avg_fault)
        results['cb2_trip_s'].append(trip_t)

        print(f'%Z={z_pct:.1f}  XHL={xhl:.4f}  '
              f'V650={avg_v:.4f}pu  '
              f'Ifault={avg_fault:.0f}A  '
              f'tCB2={trip_t:.3f}s')

    return results

def plot_sweep(results):
    """Generate three-panel sensitivity sweep plot."""
    z_vals = results['z_pct']
    design_z = DESIGN_PCT_Z

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel 1: Bus 650 voltage vs %Z
    ax1 = axes[0]
    ax1.plot(z_vals, results['bus650_v_pu'], 'b-o', linewidth=2, markersize=5)
    ax1.axvline(x=design_z, color='green', linestyle='--',
                linewidth=1.5, label=f'Design point ({design_z}%)')
    ax1.axhline(y=0.95, color='red', linestyle='--',
                linewidth=1, alpha=0.7, label='ANSI lower limit')
    ax1.axhline(y=1.05, color='red', linestyle='--',
                linewidth=1, alpha=0.7, label='ANSI upper limit')
    ax1.set_xlabel('Bridge Transformer %Z')
    ax1.set_ylabel('Bus 650 Voltage (pu)')
    ax1.set_title('Bus 650 Voltage vs Bridge %Z')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Fault current vs %Z
    ax2 = axes[1]
    ax2.plot(z_vals, results['fault_i_a'], 'r-o', linewidth=2, markersize=5)
    ax2.axvline(x=design_z, color='green', linestyle='--',
                linewidth=1.5, label=f'Design point ({design_z}%)')
    ax2.set_xlabel('Bridge Transformer %Z')
    ax2.set_ylabel('Fault Current at Bus 650 (A)')
    ax2.set_title('Fault Current vs Bridge %Z')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Panel 3: CB2 trip time vs %Z
    ax3 = axes[2]
    ax3.plot(z_vals, results['cb2_trip_s'], 'g-o', linewidth=2, markersize=5)
    ax3.axvline(x=design_z, color='green', linestyle='--',
                linewidth=1.5, label=f'Design point ({design_z}%)')
    ax3.axhline(y=0.3, color='orange', linestyle='--',
                linewidth=1, alpha=0.7, label='Min CB2 trip target (0.3s)')
    ax3.set_xlabel('Bridge Transformer %Z')
    ax3.set_ylabel('CB2 Trip Time (s)')
    ax3.set_title('CB2 Trip Time vs Bridge %Z')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    fig.suptitle(
        'Sensitivity Sweep: Bridge Transformer %Z\n'
        'Combined Substation + IEEE 13-Bus Feeder\n'
        f'%R held constant at {PCT_R}% | '
        f'Design point: {design_z}% per IEEE C57.12.36-2017',
        fontsize=10
    )

    plt.tight_layout()
    output = os.path.join(RESULTS_DIR, 'sensitivity_bridge_z.png')
    plt.savefig(output, dpi=300)
    print(f'\nPlot saved to: {output}')


def save_sweep_csv(results):
    """Export sweep results to CSV."""
    import csv
    output = os.path.join(RESULTS_DIR, 'sensitivity_bridge_z.csv')
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['PCT_Z', 'XHL', 'Bus650_V_pu',
                        'FaultI_A', 'CB2_Trip_s'])
        for i in range(len(results['z_pct'])):
            writer.writerow([
                results['z_pct'][i],
                results['xhl'][i],
                results['bus650_v_pu'][i],
                results['fault_i_a'][i],
                results['cb2_trip_s'][i],
            ])
    print(f'CSV saved to: {output}')


if __name__ == '__main__':
    print('=' * 60)
    print('SENSITIVITY SWEEP: Bridge Transformer %Z')
    print(f'Range: {Z_MIN}% to {Z_MAX}% in {Z_STEP}% steps')
    print(f'Design point: {DESIGN_PCT_Z}% (IEEE C57.12.36-2017)')
    print('=' * 60)
    print()

    results = run_sweep()
    print()
    save_sweep_csv(results)
    plot_sweep(results)

    print()
    print('=' * 60)
    print('SWEEP COMPLETE')
    print('=' * 60)