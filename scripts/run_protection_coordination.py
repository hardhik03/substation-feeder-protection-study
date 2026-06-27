import os
import sys
import math
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── IEEE C37.112-1996 Moderately Inverse (U1) curve constants ─────
# Source: Stojanovic & Djuric, Journal of Electrical Engineering,
# Vol 65, No.4, 2014, Table 1 — confirming IEEE C37.112-1996 Table 1
A = 0.0515
B = 0.1140
p = 0.02

# ── Relay settings ────────────────────────────────────────────────
# CB1: 13.8kV main breaker at SubstationBus
# Pickup = 1.5 × T1 full load current (418A) per IEEE 242
CB1 = {'name': 'CB1 (SubstationBus 13.8kV)', 'Ip': 630,  'TD': 0.5}

# CB2: 4.16kV feeder breaker at Bus 650
# Pickup = 1.5 × bridge transformer full load current (1040A) per IEEE 242
CB2 = {'name': 'CB2 (Bus 650 4.16kV)',       'Ip': 1560, 'TD': 0.2}

# ── Fault currents from short circuit study (referred to 13.8kV) ──
FAULT_CURRENTS = {
    'SubstationBus': 5068,
    'Bus650_referred': int(8677 * (4.16/13.8)),
}

CTI_MIN = 0.3  # seconds, per IEEE 242-2001

def trip_time(I, Ip, TD):
    """Calculate the trip time for a given current using the IEEE C37.112-1996 Moderately Inverse (U1) curve."""
    if I <= Ip:
        return float('inf')  # No trip if current is below pickup
    else:
        return TD * (A / ((I / Ip) ** p - 1) + B)
    
def check_coordination(cb_upstream, cb_downstream, fault_current_13kv, label):
    """Check coordination between upstream and downstream circuit breakers for a given fault current."""
    I_upstream = fault_current_13kv
    I_downstream = fault_current_13kv * (13.8/4.16)  # Convert to downstream voltage level 
    
    t_upstream = trip_time(I_upstream, cb_upstream['Ip'], cb_upstream['TD'])
    t_downstream = trip_time(I_downstream, cb_downstream['Ip'], cb_downstream['TD'])

    coordination_margin = t_upstream - t_downstream

    status = 'PASS' if coordination_margin >= CTI_MIN else 'FAIL'

    print(f"Coordination Check for {label}:")
    print(f"  Upstream CB: {cb_upstream['name']}, Trip Time: {t_upstream:.3f} s")
    print(f"  Downstream CB: {cb_downstream['name']}, Trip Time: {t_downstream:.3f} s")
    print(f"  Coordination Margin (Up - Down): {coordination_margin:.3f} s -> {status}")
    print()
    return status == 'PASS'
    

def run_coordination_check():
    print('=' * 60)
    print('PROTECTION COORDINATION STUDY')
    print('IEEE 242-2001 CTI Requirement: >= 0.3 seconds')
    print('Curve: IEEE C37.112 U1 Moderately Inverse')
    print('=' * 60)
    print()

    all_pass = True

    # Check at maximum fault current (worst case for coordination)
    result1 = check_coordination(
        CB1, CB2,
        FAULT_CURRENTS['Bus650_referred'],
        'Scenario 1: Fault at Bus 650 (maximum feeder fault current)'
    )

    # Check at minimum fault current (worst case for sensitivity)
    result2 = check_coordination(
        CB1, CB2,
        FAULT_CURRENTS['Bus650_referred'] // 2,
        'Scenario 2: Fault at mid-feeder (reduced fault current)'
    )

    all_pass = result1 and result2

    print('=' * 60)
    print('OVERALL RESULT:', 'PASS' if all_pass else 'FAIL')
    print('=' * 60)

    return all_pass

def plot_tcc():
    """Generate Time-Current Coordination plot for CB1 and CB2."""
    
    # Current range for plotting (in amps, primary at 13.8kV)
    currents = np.logspace(np.log10(500), np.log10(10000), 500)
    
    t_CB1 = []
    t_CB2 = []
    
    for I in currents:
        # CB1 sees 13.8kV current directly
        t_CB1.append(trip_time(I, CB1['Ip'], CB1['TD']))
        
        # CB2 sees current referred to 4.16kV side
        I_4kv = I * (13.8 / 4.16)
        t_CB2.append(trip_time(I_4kv, CB2['Ip'], CB2['TD']))
    
    # Replace infinity with None for clean plotting
    t_CB1 = [t if t != float('inf') else None for t in t_CB1]
    t_CB2 = [t if t != float('inf') else None for t in t_CB2]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.loglog(currents, t_CB1, 'b-', linewidth=2, label=f'CB1 — {CB1["name"]}\nIp={CB1["Ip"]}A, TD={CB1["TD"]}')
    ax.loglog(currents, t_CB2, 'r-', linewidth=2, label=f'CB2 — {CB2["name"]}\nIp={CB2["Ip"]}A, TD={CB2["TD"]}')
    
    # Mark fault currents from short circuit study
    for label, I_fault in FAULT_CURRENTS.items():
        t1 = trip_time(I_fault, CB1['Ip'], CB1['TD'])
        I_4kv = I_fault * (13.8/4.16)
        t2 = trip_time(I_4kv, CB2['Ip'], CB2['TD'])
        
        if t1 != float('inf'):
            ax.plot(I_fault, t1, 'bs', markersize=8)
        if t2 != float('inf'):
            ax.plot(I_fault, t2, 'rs', markersize=8)
        
        # Draw CTI arrow between the two points
        if t1 != float('inf') and t2 != float('inf'):
            ax.annotate('', 
                xy=(I_fault * 1.05, t2),
                xytext=(I_fault * 1.05, t1),
                arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
            ax.text(I_fault * 1.1, (t1 + t2)/2,
                   f'CTI={t1-t2:.2f}s', color='green', fontsize=8)
    
    # ANSI limits
    ax.axhline(y=0.3, color='gray', linestyle=':', alpha=0.5, label='Min CTI = 0.3s')
    
    ax.set_xlabel('Current (A) — referred to 13.8kV', fontsize=11)
    ax.set_ylabel('Operating Time (seconds)', fontsize=11)
    ax.set_title('Time-Current Coordination\nSubstation + IEEE 13-Bus Feeder Protection\n'
                 'Curve: IEEE C37.112 U1 Moderately Inverse | Ref: IEEE 242-2001',
                 fontsize=11)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, which='both', alpha=0.3)
    ax.set_xlim([500, 10000])
    ax.set_ylim([0.05, 100])
    
    output = os.path.join(RESULTS_DIR, 'tcc_coordination.png')
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    print(f'\nTCC plot saved to: {output}')


if __name__ == '__main__':
    passed = run_coordination_check()
    plot_tcc()