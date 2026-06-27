import os
import sys
import opendssdirect as dss
import matplotlib.pyplot as plt

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_24hr_loadflow():
    os.chdir(MODELS_DIR)

    # Compile without solving first
    dss.Text.Command('Compile master_combined.dss')

    # Set up daily mode before any solve
    dss.Text.Command('Set mode=daily stepsize=1h number=1')

    buses_to_monitor = ['SubstationBus', '650', '632', '671', '675', '652']
    results = {bus: [] for bus in buses_to_monitor}

    print('Running 24-hour time-series load flow...')
    print()

    for hour in range(24):
        dss.Text.Command('Solve')

        for bus in buses_to_monitor:
            dss.Circuit.SetActiveBus(bus)
            vmag = dss.Bus.puVmagAngle()[::2]
            avg_v = sum(vmag) / len(vmag)
            results[bus].append(round(avg_v, 4))

        print(f'Hour {hour:02d}: SubstationBus={results["SubstationBus"][hour]:.4f} pu  '
              f'Bus650={results["650"][hour]:.4f} pu  '
              f'Bus671={results["671"][hour]:.4f} pu')

    return results 

def check_ansi_limits(results):
    print()
    print('--- ANSI C84.1 Range A Voltage Check (0.95 - 1.05 pu) ---')
    violations = []

    for bus, voltages in results.items():
        for hour, v in enumerate(voltages):
            if v < 0.95 or v > 1.05:
                violations.append(f'Bus {bus} Hour {hour:02d}: {v:.4f} pu')

    if violations:
        print('VIOLATIONS FOUND:')
        for v in violations:
            print(f'  ✗ {v}')
    else:
        print('All buses within ANSI C84.1 limits across all 24 hours ✅')


def plot_voltage_profile(results):
    hours = list(range(24))
    plt.figure(figsize=(12, 6))

    for bus, voltages in results.items():
        plt.plot(hours, voltages, marker='o', markersize=3, label=bus)

    plt.axhline(y=1.05, color='red', linestyle='--', linewidth=1, label='ANSI Upper (1.05)')
    plt.axhline(y=0.95, color='red', linestyle='--', linewidth=1, label='ANSI Lower (0.95)')
    plt.xlabel('Hour of Day')
    plt.ylabel('Voltage (per-unit)')
    plt.title('24-Hour Voltage Profile — Combined Substation + IEEE 13-Bus Feeder\nLoad shape: EIA WACM Real Demand Data')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.xticks(hours)
    plt.tight_layout()

    output = os.path.join(RESULTS_DIR, 'voltage_profile_24hr.png')
    plt.savefig(output, dpi=300)
    print(f'\nPlot saved to: {output}')


if __name__ == '__main__':
    results = run_24hr_loadflow()
    check_ansi_limits(results)
    plot_voltage_profile(results)